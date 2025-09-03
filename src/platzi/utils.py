import asyncio
import re
from pathlib import Path

import aiofiles
import rnet

from playwright.async_api import Page
from unidecode import unidecode
from .constants import HEADERS
from .logger import Logger
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

    :param url(str): The Platzi course URL.
    :return str: The course slug.
    :raises Exception: If the URL is not a valid Platzi course URL.

    Example
    -------
    >>> get_course_slug("https://platzi.com/cursos/fastapi-2023/")
    "fastapi-2023"
    """
    pattern = r"https://platzi\.com/cursos/([^/]+)/?"
    match = re.search(pattern, url)
    if not match:
        raise Exception("Invalid course url")
    return match.group(1)


def clean_string(text: str) -> str:
    """
    Remove special characters from a string and strip it.

    :param text(str): string to clean
    :return str: cleaned string

    Example
    -------
    >>> clean_string("   Hi:;<>?{}|"")
    "Hi"
    """
    result = re.sub(r"[ºª\n\r]|[^\w\s]", "", text)
    return re.sub(r"\s+", " ", result).strip()


def slugify(text: str) -> str:
    """
    Slugify a string, removing special characters and replacing
    spaces with hyphens.

    :param text(str): string to convert
    :return str: slugified string

    Example
    -------
    >>> slugify(""Café! Frío?"")
    "cafe-frio"
    """
    return unidecode(clean_string(text)).lower().replace(" ", "-")


def get_m3u8_url(content: str) -> str:
    pattern = r"https?://[^\s\"'}]+\.m3u8"
    matches = re.findall(pattern, content)

    if not matches:
        raise Exception("No m3u8 urls found")

    return matches[0] # retorna solo una url .m3u8 si hay varios iguales


def get_subtitles_url(content: str) -> list[str] | None:
    pattern = r"https?://[^\s\"'}]+\.vtt"
    #matches = re.findall(pattern, content)
    matches = list(set(re.findall(pattern, content))) # --- NEW FEATURES: list of subtitles ---
    
    if not matches:
        return None

    return matches # retorna una lista con todos los subtitulos encontrados.
    

@retry()
async def download(url: str, path: Path, **kwargs):
    overwrite = kwargs.get("overwrite", False)

    if not overwrite and path.exists():
        return

    try:
        path.unlink(missing_ok=True)
        path.parent.mkdir(parents=True, exist_ok=True)

        client = rnet.Client(impersonate=rnet.Impersonate.Firefox139)
        response: rnet.Response = await client.get(url, allow_redirects=True, **kwargs)
        
        # print("Status Code: ", response.status)
        # print("Headers: ", response.headers)
        # print("Response URL: ", response.url)
    
        if not response.ok:
            raise Exception(f"[Bad Response: {response.status}]")

        async with aiofiles.open(path, "wb") as file:
            async with response.stream() as streamer:
                async for chunk in streamer:
                    await file.write(chunk)

    except Exception as e:
        # NO lanzar excepción — para no detener el script y continuar si falla la descarga
        #raise Exception(f"Error downloading file: [{path.name}]") from e
           
        Logger.error(f"Downloading file {url} -> {path.name} | {e}")
        
        return

    finally:
        response.close()

# --- NEW FEATURES: function download styles ---
@retry()
async def download_styles(url: str, **kwargs):
    
    client = rnet.Client(impersonate=rnet.Impersonate.Firefox139)
    response: rnet.Response = await client.get(url, allow_redirects=True, **kwargs)
        
    # Guarda el contenido antes de cerrar
    content = await response.text()
    response.close()
    
    return content  # Devuelve el contenido de la hoja de estilo
