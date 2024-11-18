import asyncio
import re
from pathlib import Path

import aiohttp
from playwright.async_api import Page
from unidecode import unidecode

from .constants import SESSION_DIR
from .helpers import read_json, write_json


async def progressive_scroll(
    page: Page, time: float = 3, delay: float = 0.1, steps: int = 250
):
    delta, total_time = 0.0, 0.0
    while total_time < time:
        await asyncio.sleep(delay)
        await page.mouse.wheel(0, steps)
        delta += steps
        total_time += delay


def get_course_slug(url: str) -> str:
    """
    Extracts the course slug from a Platzi course URL.

    Args:
        url (str): The Platzi course URL.

    Returns:
        str: The course slug.

    Raises:
        Exception: If the URL is not a valid Platzi course URL.
    """
    pattern = r"https://platzi\.com/cursos/([^/]+)/?"
    match = re.search(pattern, url)
    if not match:
        raise Exception("Invalid course url")
    return match.group(1)


def clean_string(text: str) -> str:
    """
    Cleans the input string by removing special characters and
    leading/trailing white spaces.

    Args:
        text (str): The input string to be cleaned.

    Returns:
        str: The cleaned string, with special characters removed and
        leading/trailing spaces stripped.
    """
    pattern = r"[ºª]|[^\w\s]"
    return re.sub(pattern, "", text).strip()


def slugify(text: str) -> str:
    """
    Slugify a string by removing special characters and
    leading/trailing white spaces, and replacing spaces with hyphens.

    Args:
        text (str): The input string to be slugified.
    Returns:
        str: The slugified string.
    """
    return unidecode(clean_string(text)).lower().replace(" ", "-")


def get_m3u8_url(content: str) -> str:
    pattern = r"https?://[^\s\"'}]+\.m3u8"
    matches = re.findall(pattern, content)

    if not matches:
        raise Exception("No m3u8 urls found")

    return matches[0]


def get_subtitles_url(content: str) -> str | None:
    pattern = r"https?://[^\s\"'}]+\.vtt"
    matches = re.findall(pattern, content)

    if not matches:
        return None

    return matches[0]


async def download(url: str, path: Path, **kwargs):
    overrides = kwargs.get("overrides", False)
    headers = kwargs.get("headers", None)

    if not overrides and path.exists():
        return

    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Error downloading file: [{path.name}]")

            with open(path.as_posix(), "wb") as file:
                async for chunk in response.content.iter_chunked(1024):
                    file.write(chunk)


class Cache:
    @classmethod
    def get(cls, id: str) -> dict | None:
        path = SESSION_DIR / f"{id}.json"
        try:
            return read_json(path.as_posix())
        except Exception:
            return None

    @classmethod
    def set(cls, id: str, content: dict) -> None:
        path = SESSION_DIR / f"{id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            write_json(path.as_posix(), content)
        except Exception:
            pass
