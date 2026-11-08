import asyncio
import functools
import hashlib
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urljoin

import aiofiles
import rnet
from tqdm.asyncio import tqdm

from .constants import HEADERS
from .helpers import retry
from .logger import Logger


def ffmpeg_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not shutil.which("ffmpeg"):
            raise Exception("ffmpeg is not installed")
        return await func(*args, **kwargs)

    return wrapper


def _hash_id(input: str) -> str:
    hash_object = hashlib.sha256(input.encode("utf-8"))
    return hash_object.hexdigest()


def _playlist_uri_lines(content: str, base_url: str) -> list[str]:
    return [
        urljoin(base_url, line.strip().strip('"'))
        for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


@dataclass(frozen=True)
class _Variant:
    url: str
    height: int
    bandwidth: int


def _extract_variants(content: str, base_url: str) -> list[_Variant]:
    variants: list[_Variant] = []
    attributes = None
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("#EXT-X-STREAM-INF:"):
            attributes = line.split(":", 1)[1]
        elif attributes is not None and line and not line.startswith("#"):
            resolution = re.search(r"(?:^|,)RESOLUTION=\d+x(\d+)(?:,|$)", attributes)
            bandwidth = re.search(r"(?:^|,)BANDWIDTH=(\d+)(?:,|$)", attributes)
            variants.append(
                _Variant(
                    urljoin(base_url, line.strip('"')),
                    int(resolution[1]) if resolution else 0,
                    int(bandwidth[1]) if bandwidth else 0,
                )
            )
            attributes = None
    return variants


def _select_variant(variants: list[_Variant], height: int) -> _Variant:
    at_or_below = [variant for variant in variants if 0 < variant.height <= height]
    if at_or_below:
        return max(at_or_below, key=lambda variant: (variant.height, variant.bandwidth))

    above = [variant for variant in variants if variant.height > height]
    if above:
        return min(above, key=lambda variant: (variant.height, -variant.bandwidth))

    return max(variants, key=lambda variant: variant.bandwidth)


def _video_height(path: Path) -> int | None:
    probe = shutil.which("ffprobe")
    if probe is None:
        raise RuntimeError("Se necesita ffprobe para verificar la resolución del MP4.")
    result = subprocess.run(
        [
            probe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=height",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    height = result.stdout.strip()
    return int(height) if result.returncode == 0 and height.isdecimal() else None


async def _ts_dl(url: str, path: Path, **kwargs):
    overwrite = kwargs.get("overwrite", False)

    if not overwrite and path.exists():
        return

    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)

    client = rnet.Client(impersonate=rnet.Impersonate.Chrome131)
    response: rnet.Response = await client.get(url, headers=HEADERS)

    try:
        if not response.ok:
            raise Exception("Error downloading from .ts url")

        async with aiofiles.open(path, "wb") as file:
            async with response.stream() as streamer:
                async for chunk in streamer:
                    await file.write(chunk)

    except Exception:
        raise

    finally:
        await response.close()


async def _worker_ts_dl(urls: list, dir: Path, **kwargs):
    BATCH_SIZE = 5
    IDX = 1

    bar_format = "{desc} |{bar}|{percentage:3.0f}% [{n_fmt}/{total_fmt} fragments] [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
    with tqdm(
        total=len(urls),
        desc="Progress",
        colour="green",
        bar_format=bar_format,
        ascii="░█",
    ) as bar:
        for i in range(0, len(urls), BATCH_SIZE):
            urls_batch = urls[i : i + BATCH_SIZE]
            tasks = []
            for ts_url in urls_batch:
                ts_path = dir / f"{IDX}.ts"
                tasks.append(_ts_dl(ts_url, ts_path, **kwargs))
                IDX += 1

            try:
                await asyncio.gather(*tasks)
            except Exception:
                raise Exception("Error downloading ts m3u8")

            bar.update(len(urls_batch))


@retry()
async def _m3u8_dl(
    url: str,
    path: str | Path,
    **kwargs,
) -> None:
    path = path if isinstance(path, Path) else Path(path)
    overwrite = kwargs.get("overwrite", False)
    tmp_dir = kwargs.get("tmp_dir", ".tmp")
    tmp_dir = tmp_dir if isinstance(tmp_dir, Path) else Path(tmp_dir)

    if not overwrite and path.exists():
        return

    hash = _hash_id(url)

    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    client = rnet.Client(impersonate=rnet.Impersonate.Chrome131)
    response: rnet.Response = await client.get(url, headers=HEADERS)

    try:
        if not response.ok:
            raise Exception("Error downloading m3u8")

        ts_urls = _playlist_uri_lines(await response.text(), url)

        if not ts_urls:
            raise Exception("No ts urls found")

        dir = Path(tmp_dir) / _hash_id(url)

        await _worker_ts_dl(ts_urls, dir, **kwargs)

    except Exception:
        raise

    finally:
        await response.close()

    ts_files = os.listdir(dir)
    ts_files = [ts for ts in ts_files if ts.endswith(".ts")]
    ts_files = sorted(ts_files, key=lambda x: int(x.split(".")[0]))
    ts_paths = [Path(hash) / ts for ts in ts_files]

    list_file = Path(tmp_dir) / f"{hash}.txt"
    with open(list_file.as_posix(), "w") as file:
        for ts_path in ts_paths:
            file.write(f"file '{ts_path.as_posix()}'\n")

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file.as_posix(),
        "-c",
        "copy",
        "-y" if overwrite else "-n",
        path,
    ]

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        list_file.unlink(missing_ok=True)
        shutil.rmtree(dir)

    except Exception:
        raise Exception("Error converting m3u8 to mp4")


@ffmpeg_required
async def m3u8_dl(
    url: str,
    path: str | Path,
    **kwargs,
) -> None:
    """
    Download a m3u8 file and convert it to mp4.

    :param url(str): The URL of the m3u8 file to download.
    :param path(str): The path to save the converted mp4 file.
    :param tmp_dir(str | Path): The directory to save the temporary files.
    :param kwargs: Additional keyword arguments to pass to the requests client.
    :return: None
    """

    height = int(kwargs.get("quality", "720"))

    overwrite = kwargs.get("overwrite", False)
    path = path if isinstance(path, Path) else Path(path)

    if not overwrite and path.exists():
        if height == 1080:
            actual = _video_height(path)
            if actual == height:
                Logger.info(f"Archivo existente verificado en 1080p: {path.name}")
            else:
                quality = f"{actual}p" if actual else "una resolución sin verificar"
                Logger.warning(
                    f"{path.name} está en {quality}. "
                    "Usa --overwrite para intentar descargarlo en 1080p."
                )
            return
        Logger.info(
            f"Archivo existente conservado: {path.name}. "
            "Usa --overwrite para volver a descargarlo."
        )
        return

    client = rnet.Client(impersonate=rnet.Impersonate.Chrome131)
    response: rnet.Response = await client.get(url, headers=HEADERS)

    try:
        if not response.ok:
            raise Exception("Error downloading m3u8")

        variants = _extract_variants(await response.text(), url)
        if not variants:
            raise Exception("No m3u8 urls found")

        selected = _select_variant(variants, height)
        if height == 1080:
            if selected.height and selected.height != height:
                Logger.warning(
                    f"1080p no disponible para {path.name}. "
                    f"Descargando en {selected.height}p."
                )
            elif not selected.height:
                Logger.warning(
                    f"La lista de {path.name} no indica resoluciones. "
                    "Se elige la variante de mayor ancho de banda y se verifica el MP4."
                )
            if shutil.which("ffprobe") is None:
                raise RuntimeError(
                    "Se necesita ffprobe para verificar la resolución del MP4."
                )
            path.parent.mkdir(parents=True, exist_ok=True)
            with TemporaryDirectory(dir=path.parent) as staging:
                staged = Path(staging) / "video.mp4"
                await _m3u8_dl(selected.url, staged, **kwargs)
                actual = _video_height(staged)
                if not actual or (selected.height and actual != selected.height):
                    raise RuntimeError(
                        f"El MP4 de {path.name} no coincide con la resolución "
                        "seleccionada o no se pudo verificar."
                    )
                if not overwrite and path.exists():
                    Logger.warning(
                        f"El archivo apareció durante la descarga: {path.name}."
                    )
                    return
                staged.replace(path)
            Logger.info(f"MP4 verificado en {actual}p: {path.name}")
            return
        if selected.height == height:
            Logger.info(f"Calidad seleccionada: {selected.height}p")
        elif selected.height:
            Logger.warning(
                f"{height}p no disponible. Descargando en {selected.height}p."
            )
        else:
            Logger.warning(
                f"No se pudo confirmar {height}p: la lista no indica resoluciones."
            )
        await _m3u8_dl(selected.url, path, **kwargs)

    except Exception:
        raise

    finally:
        await response.close()
