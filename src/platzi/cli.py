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
):
    """
    Download a Platzi course from the given URL.

    Arguments:
        url: str - The URL of the course to download.

    Usage:
        platzi download <url>

    Example:
        platzi download https://platzi.com/cursos/fastapi-2023/
    """
    asyncio.run(_download(url))


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


async def _download(url: str):
    async with AsyncPlatzi() as platzi:
        await platzi.download(url)
