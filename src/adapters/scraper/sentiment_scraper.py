from collections import defaultdict
import requests
from bs4 import BeautifulSoup, element


class SentimentScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0"
        }
        self.url = "https://www.myfxbook.com/community/outlook"

    async def scrape(self):
        """Gets the sentiment data from myfxbook"""
        page = requests.get(self.url, headers=self.headers, verify=False)
        self.soup = BeautifulSoup(page.content, "html.parser")
        elements = self.soup.find_all("tr", {"class": "outlook-symbol-row"})
        list_of_sentiments = defaultdict(dict)
        for element in elements:
            progress = element.find("div", {"class": "progress"})
            short = progress.find("div", {"class": "progress-bar progress-bar-danger"})
            long = progress.find("div", {"class": "progress-bar progress-bar-success"})
            currency = element.a.get_text().strip()
            short = float("".join(filter(str.isdigit, short.attrs["style"])))
            long = float("".join(filter(str.isdigit, long.attrs["style"])))
            list_of_sentiments[currency] = {
                "short": short,
                "long": long,
            }
        return list_of_sentiments
