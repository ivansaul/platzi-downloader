import functools
import json
from pathlib import Path

from playwright.async_api import BrowserContext, Page, async_playwright

from .collectors import get_chapters_urls, get_course_title, get_unit
from .constants import HEADERS, LOGIN_DETAILS_URL, LOGIN_URL, SESSION_FILE
from .helpers import read_json, write_json
from .logger import Logger
from .m3u8 import m3u8_dl
from .models import TypeUnit, User
from .utils import download, progressive_scroll, slugify


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
            Logger.info(f"Hi, {self.user.username}!")

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
        Logger.print(course_title, "[COURSE]")

        # download directory
        DL_DIR = Path("Platzi") / slugify(course_title)
        DL_DIR.mkdir(parents=True, exist_ok=True)

        # save page as mhtml
        await self.save_page(
            page,
            path=DL_DIR / "presentation.mhtml",
        )

        # iterate over chapters
        chapters_urls = await get_chapters_urls(page)
        for idx, (title, urls) in enumerate(chapters_urls, 1):
            print(f"{title}")

            CHAP_DIR = DL_DIR / f"{idx:02}_{slugify(title)}"
            CHAP_DIR.mkdir(parents=True, exist_ok=True)

            # iterate over units
            for jdx, unit_url in enumerate(urls, 1):
                unit = await get_unit(self.context, unit_url)
                name = f"{jdx:02}_{slugify(unit.title)}"

                # download video
                if unit.video:
                    dst = CHAP_DIR / f"{name}.mp4"
                    Logger.print(f"[{name}.mp4]", "[DOWNLOADING][VIDEO]")
                    await m3u8_dl(unit.video.url, dst.as_posix(), headers=HEADERS)

                    if unit.video.subtitles_url:
                        dst = CHAP_DIR / f"{name}.vtt"
                        Logger.print(f"[{name}.vtt]", "[DOWNLOADING][SUBTITLES]")
                        await download(unit.video.subtitles_url, dst)

                # download lecture
                if unit.type == TypeUnit.LECTURE:
                    Logger.print(f"[{name}.mhtml]", "[DOWNLOADING][LECTURE]")
                    await self.save_page(
                        unit.url,
                        path=CHAP_DIR / f"{name}.mhtml",
                    )

            print("=" * 100)

    @try_except_request
    async def save_page(self, src: str | Page, path: str = "source.mhtml"):
        if isinstance(src, str):
            page = await self.page
            await page.goto(src)
        else:
            page = src

        await progressive_scroll(page)

        try:
            client = await page.context.new_cdp_session(page)
            response = await client.send("Page.captureSnapshot")
            with open(path, "w", encoding="utf-8", newline="\n") as file:
                file.write(response["data"])
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
