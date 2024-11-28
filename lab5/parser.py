import requests
from bs4 import BeautifulSoup
from debugpy.common.log import warning
from fake_useragent import UserAgent

def get_random_headers():
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept-Language': 'en-GB,en;uk;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'close',
        'DNT': '1'
    }

class Parser:
    def extract_content(self, url):
        raise NotImplementedError("Цей метод повинен бути реалізований у класі-нащадку")

class ScenarioParser(Parser):
    def extract_content(self, url):
        try:
            headers = get_random_headers()
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            print(soup)
            script = soup.find('td', class_='scrtext')
            print(script)
            if script:
                return script.get_text(separator='\n')
            else:
                return "Не вдалося знайти текст статті."
        except requests.exceptions.RequestException as e:
            return f"Помилка при завантаженні сторінки: {e}"

class NewsParser(Parser):
    def extract_content(self, url):
        articles = []
        try:
            headers = get_random_headers()
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            text = ""

            if "www.bbc.com" in str(url):
                articles = soup.findAll('article')
            elif "grnt.media" in str(url):
                print("Cтаття з Сайту новин `ГРУНТ`")
                articles = soup.findAll('div', class_='inner-post-entry')

            elif "unian.ua" in str(url):
                print("Cтаття з Сайту новин `UNIAN`")
                articles = soup.findAll('div', class_='article-text')

            for article in articles:
                if article:
                    text += " " + str(article.get_text(separator='\n'))

            if text:
                return text
            else:
                warning("Не вдалося знайти текст статті")
                return None
        except requests.exceptions.RequestException as e:
            warning(f"Помилка при завантаженні сторінки: {e}")
            return None

class ArticleParser(Parser):
    def extract_content(self, url):

        return "Текст наукової статті з URL: " + url