import asyncio
from playwright.async_api import BrowserContext, Page

from .cache import Cache
from .constants import PLATZI_URL
from .models import Chapter, TypeUnit, Unit, Video, Resource
from .utils import get_m3u8_url, get_subtitles_url, slugify, download_styles


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
    # Alternative: '//h4[normalize-space(text())="Archivos de la clase"]/following-sibling::ul[1]//a[@class="FilesAndLinks_Item__fR7g4"]'
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


        # --- NEW FEATURES: OBTENER RECURSOS Y RESUMEN ---
        
        files_section = page.locator(SECTION_FILES)
        next_sibling_files = files_section.locator(SIBLINGS)
        
        reading_section = page.locator(SECTION_READING)
        next_sibling_reading = reading_section.locator(SIBLINGS)
        
        download_all_button = page.locator(BUTTON_DOWNLOAD_ALL)
        
        file_links = []
        readings_links = []
        
        # Obtener "Archivos de la clase" si la sección existe
        if await next_sibling_files.count() > 0:
            # Dentro de la sección, buscamos todos los elementos 'a' con la clase específica
            enlaces = next_sibling_files.locator(SECTION_LINKS)
            # Iteramos sobre todos los enlaces encontrados y extraemos el atributo 'href'            
            for i in range(await enlaces.count()):
                link = await enlaces.nth(i).get_attribute('href')
                if link:
                    file_links.append(link)
        
        # Obtener link del boton descargar todo si existe
        if await download_all_button.count() > 0:
            link = await download_all_button.get_attribute('href')
            if link:
                file_links.append(link)

        # Obtener links de "Lecturas recomendadas" si la sección existe
        if await next_sibling_reading.count() > 0:
            enlaces = next_sibling_reading.locator(SECTION_LINKS)
            for i in range(await enlaces.count()):
                link = await enlaces.nth(i).get_attribute('href')
                if link:
                    readings_links.append(link) 

        # Obtener resumen si existe
        summary = page.locator(SUMMARY_CONTENT_SELECTOR)
        if await summary.count() > 0:
            
            all_css_styles = []
            
            # Obtener la estructura HTML del resumen
            summary_section = await summary.evaluate("el => el.outerHTML")
            
            # Buscar todos los selectores CSS para incluir en la plantilla html_summary
            stylesheet_links = page.locator("link[rel=stylesheet]")                  
            count = await stylesheet_links.count()
            for i in range(count):
                # Usa evaluate para obtener el outerHTML completo de cada link
                # stylesheet_tag = await stylesheet_links.nth(i).evaluate("el => el.outerHTML")
                
                href = await stylesheet_links.nth(i).get_attribute("href") 
                if href:
                    stylesheet = await download_styles(href) # New function: download styles 
                    all_css_styles.append(stylesheet) 
            
            # Obtener el contenido de los <style>
            style_blocks = await page.query_selector_all("style")
            for style in style_blocks:
                content = await style.inner_text()
                all_css_styles.append(content)
  
            # Combinar todos los estilos
            styles = "\n".join(filter(None, all_css_styles))
            
            # Plantilla HTML para el resumen
            html_summary = f"""
            <!DOCTYPE html>
            <html lang="es" class="__variable_ce9353">
            <head>
                <meta charset="UTF-8">
                <title>{title}</title>               
                <style>{styles}</style>
            </head>
            <body class="__className_ce9353">
                {summary_section}
            </body>
            </html>
            """
        
        await asyncio.sleep(3)
        
        return Unit(
            url=url,
            title=title,
            type=type,
            video=video,
            slug=slugify(title),
            resources=Resource(
                files_url = file_links,
                readings_url = readings_links,
                summary = html_summary
            )
        )

    except Exception:
        raise EXCEPTION

    finally:
        await page.close()
