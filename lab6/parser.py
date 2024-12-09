from logging import warning
import requests
from bs4 import BeautifulSoup
from lab5.parser import get_random_headers


class BookParser:
    def __init__(self, language, url, params=None):
        self.language = language
        self.url = url
        self.params = params or {}
        self.text = ""

    def extract_content(self):
        if "page" in self.params:
            max_page = int(self.params["page"])
            for page in range(1, max_page + 1):
                print(f"Обробляємо {page} сторінку ... ")
                self.params["page"] = page
                self.text += self._fetch_page_content()
        else:
            self.text = self._fetch_page_content()
        return self.text

    def _fetch_page_content(self):
        headers = get_random_headers()
        response = requests.get(self.url, headers=headers, params=self.params)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            if self.language == "en":
                content = soup.find("div", class_="container_wrapper").get_text()
            else: content = soup.find("article", class_="prose").get_text()
            return content
        else:
            warning(f"Не вдалося отримати дані з {self.url}")
            return ""