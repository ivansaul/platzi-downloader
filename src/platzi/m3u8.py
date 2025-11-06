import asyncio
import functools
import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import aiofiles
import rnet
from tqdm.asyncio import tqdm

from .constants import REFERER
from .helpers import retry


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


def _extract_streaming_urls(content: str) -> list[str] | None:
    BASE_URL = "https://mediastream.platzi.com"
    pattern = r"(https?://[^\s]+|(?::)?///?[^\s]+)"
    matches = re.findall(pattern, content)

    urls = []  # save video resolutions
    for match in matches:
        if match.startswith("http"):
            urls.append(match)
        else:
            full_url = BASE_URL.rstrip("/") + "/" + match.lstrip(":/")
            urls.append(full_url)

    return urls or None


async def _ts_dl(url: str, path: Path, **kwargs):
    overwrite = kwargs.get("overwrite", False)

    if not overwrite and path.exists():
        return

    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)

    client = rnet.Client(impersonate=rnet.Impersonate.Firefox139)
    response: rnet.Response = await client.get(url, headers={"Referer": REFERER})

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

    client = rnet.Client(impersonate=rnet.Impersonate.Firefox139)
    response: rnet.Response = await client.get(url, headers={"Referer": REFERER})

    try:
        if not response.ok:
            raise Exception("Error downloading m3u8")

        ts_urls = _extract_streaming_urls(await response.text())

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

    # quality selection
    quality = kwargs.get("quality", "720")

    quality = 0 if quality == "720" else 1

    overwrite = kwargs.get("overwrite", False)
    path = path if isinstance(path, Path) else Path(path)

    if not overwrite and path.exists():
        return

    client = rnet.Client(impersonate=rnet.Impersonate.Firefox139)
    response: rnet.Response = await client.get(url, headers={"Referer": REFERER})

    try:
        if not response.ok:
            raise Exception("Error downloading m3u8")

        m3u8_urls = _extract_streaming_urls(
            await response.text()
        )  # The .m3u8 link contains the video resolutions

        if not m3u8_urls:
            raise Exception("No m3u8 urls found")

        await _m3u8_dl(
            m3u8_urls[int(quality)], path, **kwargs
        )  # Here goes the video resolution [0]=1280; [1]=1920

    except Exception:
        raise

    finally:
        await response.close()
