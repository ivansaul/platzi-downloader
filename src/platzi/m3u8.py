import asyncio
import functools
import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import aiohttp
from tqdm.asyncio import tqdm

from .logger import Logger


def ffmpeg_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not shutil.which("ffmpeg"):
            Logger.error("ffmpeg is not installed")
            return
        return await func(*args, **kwargs)

    return wrapper


def _hash_id(input: str) -> str:
    hash_object = hashlib.sha256(input.encode("utf-8"))
    return hash_object.hexdigest()


async def _ts_dl(url: str, path: Path, **kwargs):
    overrides = kwargs.get("overrides", False)
    headers = kwargs.get("headers", None)

    if not overrides and path.exists():
        return

    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception("Error downloading from .ts url")
            with open(path.as_posix(), "wb") as file:
                file.write(await response.read())


async def _worker_ts_dl(urls: list, dir: Path, **kwargs):
    BATCH_SIZE = 10
    IDX = 1

    with tqdm(total=len(urls)) as bar:
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


async def _m3u8_dl(
    url: str,
    path: str,
    tmp_dir: str = ".tmp",
    **kwargs,
) -> None:
    overrides = kwargs.get("overrides", False)
    headers = kwargs.get("headers", None)

    if not overrides and Path(path).exists():
        return

    hash = _hash_id(url)

    Path(path).unlink(missing_ok=True)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception("Error downloading m3u8")

            pattern = r"https?://[^\s]+"
            ts_urls = re.findall(pattern, await response.text())

            if not ts_urls:
                raise Exception("No ts urls found")

            dir = Path(tmp_dir) / _hash_id(url)

            await _worker_ts_dl(ts_urls, dir, **kwargs)

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
        "-y" if overrides else "-n",
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


async def m3u8_dl(
    url: str,
    path: str,
    tmp_dir: str = ".tmp",
    **kwargs,
):
    # TODO: implement quality selection
    headers = kwargs.get("headers", None)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception("Error downloading m3u8")

            pattern = r"https?://[^\s]+"
            m3u8_urls = re.findall(pattern, await response.text())

            if not m3u8_urls:
                raise Exception("No m3u8 urls found")

            await _m3u8_dl(m3u8_urls[0], path, **kwargs)
