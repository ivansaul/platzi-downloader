import asyncio
import re
from pathlib import Path

import aiofiles
import rnet
from playwright.async_api import Page
from unidecode import unidecode

from .helpers import retry


async def progressive_scroll(
    page: Page, time: float = 3, delay: float = 0.1, steps: int = 250
):
    await asyncio.sleep(3)  # delay to avoid rate limiting
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


@retry()
async def download(url: str, path: Path, **kwargs):
    overwrite = kwargs.get("overwrite", False)

    if not overwrite and path.exists():
        return

    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)

    client = rnet.Client(impersonate=rnet.Impersonate.Firefox135)
    response: rnet.Response = await client.get(url, **kwargs)

    try:
        if not response.ok:
            raise Exception("[Bad Response]")

        async with aiofiles.open(path, "wb") as file:
            async with response.stream() as streamer:
                async for chunk in streamer:
                    await file.write(chunk)

    except Exception as e:
        raise Exception(f"Error downloading file: [{path.name}]") from e

    finally:
        response.close()
