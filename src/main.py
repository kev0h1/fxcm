import html5lib
import requests
from bs4 import BeautifulSoup

from src.config import ForexPairEnum, PeriodEnum
from src.fxcm_connect.fxcm_connect import FXCMConnect, config

# dummmy

if __name__ == "__main__":
    url = "https://relatedwords.io/social-media"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html5lib")
    arr = soup.find_all("a")

    f = open("social.txt", "a")
    f.write("data\n")
    for item in arr:
        try:
            f.write(item.text + "\n")
        except:
            pass

    f.close()
