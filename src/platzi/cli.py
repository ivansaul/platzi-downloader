import asyncio

import typer
from rich import print
from typing_extensions import Annotated

from platzi import AsyncPlatzi, Cache

app = typer.Typer(rich_markup_mode="rich")


@app.command()
def login():
    """
    Open a browser window to Login to Platzi.

    Usage:
        platzi login
    """
    asyncio.run(_login())


@app.command()
def logout():
    """
    Delete the Platzi session from the local storage.

    Usage:
        platzi logout
    """
    asyncio.run(_logout())


@app.command()
def download(
    url: Annotated[
        str,
        typer.Argument(
            help="The URL of the course to download",
            show_default=False,
        ),
    ],
    # TODO: Define a Quality enum (e.g. 360p, 720p, 1080p,...)
    # and use it here instead of str
    quality: Annotated[
        str,
        typer.Option(
            "--quality",
            "-q",
            help="The quality of the video to download.",
            show_default=True,
        ),
    ] = "720",
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            "-w",
            help="Overwrite files if exist.",
            show_default=True,
        ),
    ] = False,
):
    """
    Download a Platzi course from the given URL.

    Arguments:
        url: str - The URL of the course to download.

    Usage:
        platzi download <url>

    Example:
        platzi download https://platzi.com/cursos/python/
    """
    asyncio.run(_download(url, quality=quality, overwrite=overwrite))


@app.command()
def clear_cache():
    """
    Clear the Platzi CLI cache.

    Usage:
        platzi clear-cache
    """
    Cache.clear()
    print("[green]Cache cleared successfully 🗑️[/green]")


async def _login():
    async with AsyncPlatzi() as platzi:
        await platzi.login()


async def _logout():
    async with AsyncPlatzi() as platzi:
        await platzi.logout()


async def _download(url: str, **kwargs):
    async with AsyncPlatzi() as platzi:
        await platzi.download(url, **kwargs)
