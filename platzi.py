import re
from utils import *
from time import sleep

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Platzi:
    def __init__(self, email, password, url_course, headless):      
        self.email = email
        self.password = password
        self.url_course = url_course
        self.headless = headless
        self.data = {}
        self.course_name = ""
        self.videos = []
        self.url_login = "https://platzi.com/login/"

    def quit(self):
        self.driver.quit()

    def login(self):
        if self.headless:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            self.driver = uc.Chrome(options = options)
        else:
            self.driver = uc.Chrome()
        
        self.driver.get(self.url_login)
    
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//button[@type="submit"]')))
        self.driver.find_element(By.XPATH, '//input[@name="email"]').send_keys(self.email)
        self.driver.find_element(By.XPATH, '//input[@name="password"]').send_keys(self.password)
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//nav[@class="MainMenu"]')))

    def get_source_code(self):
        return self.driver.page_source

    def get_course_content(self):        
        self.driver.get(self.url_course)
      
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//span[@data-qa="course_name"]')))

        self.course_name =  self.driver.find_element(By.XPATH, '//span[@data-qa="course_name"]').text

        sections = self.driver.find_elements(By.XPATH, '//article')

        for index, section in enumerate(sections, start = 1):
            section_title = section.find_element(By.XPATH, './/span[@class="Tag_Tag__zf4J4 styles_Section__Title__qGhEE"]').text
            section_title = f'{index}. {clean_string(section_title)}'

            items = section.find_elements(By.XPATH, './/a[contains(@class, "styles_Item__PaAdo")]')
            print(f'- {section_title} [{len(items)} items]')
            
            
            for item in items:
                item_title = item.find_element(By.XPATH, './/p').text
                item_url = item.get_attribute('href')

                item_title = clean_string(item_title)
                # print(item_title)
                # print(item_url)
                
                self.videos.append({
                    'section': section_title,
                    'title': item_title,
                    'url': item_url
                })
            
            # print('=' * 20)     

    def get_m3u8_url(self):

        pattern = r'https://mdstrm\.com/video/[a-zA-Z0-9_-]+\.m3u8'
        
        j, k = 1, len(self.videos)

        for video in self.videos:
            ulr = video['url'].replace('https://platzi.com', 'https://platzi.com/new-home')
            self.driver.get(ulr)
            sleep(5)
            content = self.get_source_code()
            m3u8_urls = re.findall(pattern, content)
            if len(m3u8_urls) > 0:
                video['m3u8_url'] = m3u8_urls[0]
                print(f'[{j} / {k}][streaming] {video["title"]}')
            else:
                video['m3u8_url'] = None
                print(f'[{j} / {k}][reading] {video["title"]}')
                # Download reading as HTML file
                dir_path = f'{self.course_name}/{video["section"]}'
                file_path = f'{dir_path}/{j}. {video["title"]}.html'
                check_path(dir_path)
                write_file(file_path, content)

            j = j + 1

    def write_data(self, file_path = 'data.json'):
        self.data['name'] = self.course_name
        self.data['videos'] = self.videos
        write_json(data=self.data, file_path = file_path)

if __name__ == "__main__":
    username, password = input_credentials()
    url_course = input('Enter the URL of the course to download: ')
    if(not url_course.startswith('https://platzi.com/new-home')):
        url_course = url_course.replace('https://platzi.com', 'https://platzi.com/new-home')
    
    platzi = Platzi(username, password, url_course, headless = False)
    print('Logging in ...', end = '\n\n')
    platzi.login()
    print('Getting course content ...', end = '\n\n')
    platzi.get_course_content()
    print('Getting download urls ...', end = '\n\n')
    platzi.get_m3u8_url()
    print('Writing json data ...', end = '\n\n')
    platzi.write_data()
    platzi.quit()