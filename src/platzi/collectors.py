import asyncio

from playwright.async_api import BrowserContext, Page

from .cache import Cache
from .constants import PLATZI_URL
from .models import Chapter, Resource, TypeUnit, Unit, Video
from .utils import download_styles, get_m3u8_url, get_subtitles_url, slugify


@Cache.cache_async
async def get_course_title(page: Page) -> str:
    SELECTOR = ".CourseHeader_CourseHeader__Title__yhjgH"
    EXCEPTION = Exception("No course title found")
    try:
        title = await page.locator(SELECTOR).first.text_content()
        if not title:
            raise EXCEPTION
    except Exception:
        await page.close()
        raise EXCEPTION

    return title


@Cache.cache_async
async def get_draft_chapters(page: Page) -> list[Chapter]:
    SELECTOR = ".Syllabus_Syllabus__bVYL_ article"
    EXCEPTION = Exception("No sections found")
    try:
        locator = page.locator(SELECTOR)

        chapters: list[Chapter] = []
        for i in range(await locator.count()):
            chapter_name = await locator.nth(i).locator("h2").first.text_content()

            if not chapter_name:
                raise EXCEPTION

            block_list_locator = locator.nth(i).locator(
                ".SyllabusSection_SyllabusSection__Materials__C2hlu a"
            )

            units: list[Unit] = []
            for j in range(await block_list_locator.count()):
                ITEM_LOCATOR = block_list_locator.nth(j)

                unit_url = await ITEM_LOCATOR.get_attribute("href")
                unit_title = await ITEM_LOCATOR.locator("h3").first.text_content()

                if not unit_url or not unit_title:
                    raise EXCEPTION

                units.append(
                    Unit(
                        type=TypeUnit.VIDEO,
                        title=unit_title,
                        url=PLATZI_URL + unit_url,
                        slug=slugify(unit_title),
                    )
                )

            chapters.append(
                Chapter(
                    name=chapter_name,
                    slug=slugify(chapter_name),
                    units=units,
                )
            )

    except Exception as e:
        await page.close()
        raise EXCEPTION from e

    return chapters


@Cache.cache_async
async def get_unit(context: BrowserContext, url: str) -> Unit:
    TYPE_SELECTOR = ".VideoPlayer"
    TITLE_SELECTOR = "h1.MaterialHeading_MaterialHeading__title__sDUKY"
    EXCEPTION = Exception("Could not collect unit data")

    # --- NEW CONSTANTS ----
    SECTION_FILES = '//h4[normalize-space(text())="Archivos de la clase"]'
    SECTION_READING = '//h4[normalize-space(text())="Lecturas recomendadas"]'
    SECTION_LINKS = 'a.FilesAndLinks_Item__fR7g4'
    BUTTON_DOWNLOAD_ALL = 'a.FilesTree_FilesTree__Download__nGUsL'
    SUMMARY_CONTENT_SELECTOR = 'div.Resources_Resources__Articlass__00D6l'
    SIBLINGS = '//following-sibling::ul[1]'

    if "/quiz/" in url:
        return Unit(
            url=url,
            title="Quiz",
            type=TypeUnit.QUIZ,
            slug="Quiz",
        )

    try:
        page = await context.new_page()
        await page.goto(url)

        await asyncio.sleep(5)  # delay to avoid rate limiting

        title = await page.locator(TITLE_SELECTOR).first.text_content()

        if not title:
            raise EXCEPTION

        if not await page.locator(TYPE_SELECTOR).is_visible():
            return Unit(
                url=url,
                title=title,
                type=TypeUnit.LECTURE,
                slug=slugify(title)
            )
        else:
            content = await page.content()
            type = TypeUnit.VIDEO
            video = Video(
                url=get_m3u8_url(content),
                subtitles_url=get_subtitles_url(content),
            )

        # --- Get resources and summary---
        files_section = page.locator(SECTION_FILES)
        next_sibling_files = files_section.locator(SIBLINGS)

        reading_section = page.locator(SECTION_READING)
        next_sibling_reading = reading_section.locator(SIBLINGS)

        download_all_button = page.locator(BUTTON_DOWNLOAD_ALL)

        file_links = []
        readings_links = []

        # Get "Archivos de la clase" if the section exists
        if await next_sibling_files.count() > 0:
            enlaces = next_sibling_files.locator(SECTION_LINKS)
            for i in range(await enlaces.count()):
                link = await enlaces.nth(i).get_attribute('href')
                if link:
                    file_links.append(link)

        # Get link of the download all button if it exists
        if await download_all_button.count() > 0:
            link = await download_all_button.get_attribute('href')
            if link:
                file_links.append(link)

        # Get "Lecturas recomendadas" if the section exists
        if await next_sibling_reading.count() > 0:
            enlaces = next_sibling_reading.locator(SECTION_LINKS)
            for i in range(await enlaces.count()):
                link = await enlaces.nth(i).get_attribute('href')
                if link:
                    readings_links.append(link)

        # Get summary if it exists
        summary = page.locator(SUMMARY_CONTENT_SELECTOR)
        if await summary.count() > 0:

            all_css_styles = []

            # Get the HTML structure of the summary
            summary_section = await summary.evaluate("el => el.outerHTML")

            # Find all CSS selectors to include in the html_summary template
            stylesheet_links = page.locator("link[rel=stylesheet]")
            count = await stylesheet_links.count()
            for i in range(count):

                href = await stylesheet_links.nth(i).get_attribute("href")
                if href:
                    stylesheet = await download_styles(href)
                    all_css_styles.append(stylesheet)

            # Get the content of the <style>
            style_blocks = await page.query_selector_all("style")
            for style in style_blocks:
                content = await style.inner_text()
                all_css_styles.append(content)

            # Combine all styles
            styles = "\n".join(filter(None, all_css_styles))

            # HTML template for the summary
            html_summary = f"""
           <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{title}</title>
                <style>{styles}</style>
            </head>
            <body>
                <div class="Layout_Layout__s8xxr">
                    <main class="Layout_Layout-main__FbmEd">
                        {summary_section}
                    </main>
                </div>
            </body>
            </html>"""

        return Unit(
            url=url,
            title=title,
            type=type,
            video=video,
            slug=slugify(title),
            resources=Resource(
                files_url=file_links,
                readings_url=readings_links,
                summary=html_summary
            )
        )

    except Exception:
        raise EXCEPTION

    finally:
        await page.close()
