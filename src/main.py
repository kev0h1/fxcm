from src.config import ForexPairEnum, PeriodEnum
from src.fxcm_connect.fxcm_connect import FXCMConnect, config
from bs4 import BeautifulSoup
import requests
import html5lib


if __name__ == "__main__":
    url = "https://relatedwords.io/weight-loss"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html5lib")
    arr = soup.find_all("a")

    f = open("my_data2.txt", "a")
    f.write("data\n")
    for item in arr:
        try:
            f.write(item.text + "\n")
        except:
            pass

    f.close()
