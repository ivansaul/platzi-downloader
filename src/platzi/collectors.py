from playwright.async_api import BrowserContext, Page

from .constants import PLATZI_URL
from .models import TypeUnit, Unit, Video
from .utils import get_m3u8_url, get_subtitles_url, slugify


async def get_course_title(page: Page) -> str:
    SELECTOR = ".Hero-content-title"
    EXCEPTION = Exception("No course title found")
    try:
        title = await page.locator(SELECTOR).first.text_content()
        if not title:
            raise EXCEPTION
    except Exception:
        await page.close()
        raise EXCEPTION

    return title


async def get_chapters_urls(page: Page) -> list[tuple[str, list[str]]]:
    SELECTOR = ".Content-feed div.ContentBlock"
    EXCEPTION = Exception("No sections found")
    try:
        locator = page.locator(SELECTOR)
        items = []
        for i in range(await locator.count()):
            title = await locator.nth(i).locator("h3").first.text_content()

            if not title:
                raise EXCEPTION

            block_list_locator = locator.nth(i).locator(".ContentBlock-list a")

            urls: list[str] = []
            for j in range(await block_list_locator.count()):
                url = await block_list_locator.nth(j).get_attribute("href")

                if not url:
                    raise EXCEPTION

                urls.append(PLATZI_URL + url)

            items.append((title, urls))

    except Exception as e:
        await page.close()
        raise EXCEPTION from e

    return items


async def get_unit(context: BrowserContext, url: str) -> Unit:
    TYPE_SELECTOR = ".VideoPlayer"
    TITLE_SELECTOR = ".MaterialDesktopHeading_MaterialDesktopHeading-info__title__DaYr2"
    EXCEPTION = Exception("Could not collect unit data")

    try:
        page = await context.new_page()
        await page.goto(url)

        title = await page.locator(TITLE_SELECTOR).first.text_content()

        if not title:
            raise EXCEPTION

        if await page.locator(TYPE_SELECTOR).count() == 0:
            type = TypeUnit.LECTURE
            video = None

        else:
            content = await page.content()
            type = TypeUnit.VIDEO
            video = Video(
                url=get_m3u8_url(content),
                subtitles_url=get_subtitles_url(content),
            )

        return Unit(
            url=url,
            title=title,
            type=type,
            video=video,
            slug=slugify(title),
        )

    except Exception:
        raise EXCEPTION

    finally:
        await page.close()
