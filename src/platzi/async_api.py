import functools
import json
import os
import time
from pathlib import Path
from urllib.parse import unquote

import aiofiles
from playwright.async_api import BrowserContext, Page, async_playwright
from rich import box, print
from rich.live import Live
from rich.table import Table

from .collectors import get_course_title, get_draft_chapters, get_unit
from .constants import HEADERS, LOGIN_DETAILS_URL, LOGIN_URL, SESSION_FILE
from .helpers import read_json, write_json
from .logger import Logger
from .m3u8 import m3u8_dl
from .models import TypeUnit, User
from .utils import clean_string, download, progressive_scroll


def login_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        self = args[0]
        if not isinstance(self, AsyncPlatzi):
            Logger.error(f"{login_required.__name__} can only decorate Platzi class.")
            return
        if not self.loggedin:
            Logger.error("Login first!")
            return
        return await func(*args, **kwargs)

    return wrapper


def try_except_request(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        self = args[0]
        if not isinstance(self, AsyncPlatzi):
            Logger.error(
                f"{try_except_request.__name__} can only decorate Platzi class."
            )
            return

        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if str(e):
                Logger.error(e)
        return

    return wrapper


class AsyncPlatzi:
    def __init__(self, headless=False):
        self.loggedin = False
        self.headless = headless
        self.user = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context(
            java_script_enabled=True,
            is_mobile=True,
        )

        try:
            await self._load_state()
        except Exception:
            pass

        await self._set_profile()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._context.close()
        await self._browser.close()
        await self._playwright.stop()

    @property
    async def page(self) -> Page:
        return await self._context.new_page()

    @property
    def context(self) -> BrowserContext:
        return self._context

    @try_except_request
    async def _set_profile(self) -> None:
        try:
            data = await self.get_json(LOGIN_DETAILS_URL)
            self.user = User(**data)
        except Exception:
            return

        if self.user.is_authenticated:
            self.loggedin = True
            Logger.info(f"Hi, {self.user.username}!\n")

    @try_except_request
    async def login(self) -> None:
        Logger.info("Please login, in the opened browser")
        Logger.info("You have to login manually, you have 2 minutes to do it")

        page = await self.page
        await page.goto(LOGIN_URL)
        try:
            avatar = await page.wait_for_selector(
                ".styles-module_Menu__Avatar__FTuh-",
                timeout=2 * 60 * 1000,
            )
            if avatar:
                self.loggedin = True
                await self._save_state()
                Logger.info("Logged in successfully")
        except Exception:
            raise Exception("Login failed")
        finally:
            await page.close()

    @try_except_request
    async def logout(self):
        SESSION_FILE.unlink(missing_ok=True)
        Logger.info("Logged out successfully")

    @try_except_request
    @login_required
    async def download(self, url: str, **kwargs):
        page = await self.page
        await page.goto(url)

        # course title
        course_title = await get_course_title(page)
        # Logger.print(course_title, "[COURSE]")

        # download directory
        DL_DIR = Path("Courses") / clean_string(course_title)
        DL_DIR.mkdir(parents=True, exist_ok=True)

        # save page as mhtml
        presentation_path = DL_DIR / "presentation.mhtml"
        await self.save_page(page, path=presentation_path, **kwargs)

        # iterate over chapters
        draft_chapters = await get_draft_chapters(page)

        # --- Course Details Table ---
        table = Table(
            title=course_title,
            caption="processing...",
            caption_style="green",
            title_style="green",
            header_style="green",
            footer_style="green",
            show_footer=True,
            box=box.SQUARE_DOUBLE_HEAD,
        )
        table.add_column("Sections", style="green", footer="Total", no_wrap=True)
        table.add_column("Lessons", style="green", footer="0", justify="center")

        total_units = 0

        with Live(table, refresh_per_second=4):  # update 4 times a second to feel fluid
            for idx, section in enumerate(draft_chapters, 1):
                time.sleep(0.3)  # arbitrary delay
                num_units = len(section.units)
                total_units += num_units
                table.add_row(f"{idx}-{section.name}", str(len(section.units)))
                table.columns[1].footer = str(total_units)  # Update footer dynamically

        for idx, draft_chapter in enumerate(draft_chapters, 1):
            Logger.info(f"Creating directory: {draft_chapter.name}")

            CHAP_DIR = DL_DIR / f"{idx:02}-{clean_string(draft_chapter.name)}"
            CHAP_DIR.mkdir(parents=True, exist_ok=True)

            # iterate over units
            for jdx, draft_unit in enumerate(draft_chapter.units, 1):
                unit = await get_unit(self.context, draft_unit.url)
                file_name = f"{jdx:02}-{clean_string(unit.title)}"

                # download video
                if unit.video:
                    dst = CHAP_DIR / f"{file_name}.mp4"
                    Logger.print(f"[{dst.name}]", "[DOWNLOADING-VIDEO]")
                    await m3u8_dl(unit.video.url, dst, headers=HEADERS, **kwargs)

                    # download subtitles
                    subs = unit.video.subtitles_url
                    if subs:
                        for sub in subs:
                            lang = (
                                "_es"
                                if "ES" in sub
                                else "_en"
                                if "EN" in sub
                                else "_pt"
                                if "PT" in sub
                                else ""
                            )

                            dst = CHAP_DIR / f"{file_name}{lang}.vtt"
                            Logger.print(f"[{dst.name}]", "[DOWNLOADING-SUBS]")
                            await download(sub, dst, **kwargs)

                    # download resources
                    if unit.resources:
                        # download files
                        files = unit.resources.files_url
                        if files:
                            for archive in files:
                                file_name = unquote(os.path.basename(archive))
                                dst = CHAP_DIR / f"{jdx:02}-{file_name}"
                                Logger.print(f"[{dst.name}]", "[DOWNLOADING-FILES]")
                                await download(archive, dst)

                        # download readings
                        readings = unit.resources.readings_url
                        if readings:
                            dst = CHAP_DIR / f"{jdx:02}-Lecturas recomendadas.txt"
                            Logger.print(f"[{dst.name}]", "[SAVING-READINGS]")
                            with open(dst, "w", encoding="utf-8") as f:
                                for lecture in readings:
                                    f.write(lecture + "\n")

                        # download summary
                        summary = unit.resources.summary
                        if summary:
                            dst = CHAP_DIR / f"{jdx:02}-Resumen.html"
                            Logger.print(f"[{dst.name}]", "[SAVING-SUMMARY]")
                            with open(dst, "w", encoding="utf-8") as f:
                                f.write(summary)

                # download lecture
                if unit.type == TypeUnit.LECTURE:
                    dst = CHAP_DIR / f"{file_name}.mhtml"
                    Logger.print(f"[{dst.name}]", "[DOWNLOADING-LECTURE]")
                    await self.save_page(unit.url, path=dst)

                # download quiz
                if unit.type == TypeUnit.QUIZ:
                    dst = CHAP_DIR / f"{file_name}.mhtml"
                    Logger.print(f"[{dst.name}]", "[DOWNLOADING-QUIZ]")
                    await self.save_page(unit.url, path=dst)

            print("=" * 100)

    @try_except_request
    async def save_page(
        self,
        src: str | Page,
        path: str | Path = "source.mhtml",
        **kwargs,
    ):
        overwrite: bool = kwargs.get("overwrite", False)

        if not overwrite and Path(path).exists():
            return

        if isinstance(src, str):
            page = await self.page
            await page.goto(src)
        else:
            page = src

        await progressive_scroll(page)

        try:
            client = await page.context.new_cdp_session(page)
            response = await client.send("Page.captureSnapshot")
            async with aiofiles.open(path, "w", encoding="utf-8", newline="\n") as file:
                await file.write(response["data"])
        except Exception:
            raise Exception("Error saving page as mhtml")

        if isinstance(src, str):
            await page.close()

    @try_except_request
    async def get_json(self, url: str) -> dict:
        page = await self.page
        await page.goto(url)
        content = await page.locator("pre").first.text_content()
        await page.close()
        return json.loads(content or "{}")

    async def _save_state(self):
        cookies = await self.context.cookies()
        write_json(SESSION_FILE, cookies)

    async def _load_state(self):
        SESSION_FILE.touch()
        cookies = read_json(SESSION_FILE)
        await self.context.add_cookies(cookies)
