# import Packages:
import sys
import time
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from dataclasses import dataclass
from bs4 import BeautifulSoup
# ______________________________________________________________________________________________________________________
# Functions:


def create_url(basic_url: str, term: str) -> str:
    term = term.replace(" ", "+")
    return basic_url.replace("PLACEHOLDER", f"%22{term}%22")


def get_url_and_text(function_driver: webdriver) -> [[]]:
    article_elements = function_driver.find_elements(By.XPATH, RNZ_HYPERLINKS_XPATH)
    return [Article(time.localtime(), article_url.get_attribute('text'), article_url.get_attribute('href'))
            for article_url in article_elements]


def get_element(function_driver: webdriver, xpath: str = None, attribute: str = "text"):
    if xpath is not None:
        elements = function_driver.find_elements(By.XPATH, xpath)
        if len(elements) == 0:
            return None
        if len(elements) == 1:
            return elements[0].get_attribute(attribute)
        if len(elements) > 1:
            print(len(elements))
            for element in elements:
                print(element.get_attribute(attribute))
    else:
        return None


# ______________________________________________________________________________________________________________________


@dataclass
class Article:
    created: time.struct_time
    title: str
    url: str
    text: str = None
    article_type1: str = None
    article_type2: str = None
    date: str = None
    author: str = None
    author_url: str = None


URL = r"https://www.rnz.co.nz/search/results?q=PLACEHOLDER&commit=Search"
RNZ_BUTTON_XPATH = '//*[contains(concat( " ", @class, " " ), concat( " ", "next", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "btn", " " ))]'
RNZ_HYPERLINKS_XPATH = '//*[contains(concat( " ", @class, " " ), concat( " ", "faux-link", " " ))]'
type_one_xpath = '//*[@id="documentContent"]/div[2]/div/header/div[1]/div/span[1]/a'
type_two_xpath = '// *[ @ id = "documentContent"] / div[2] / div / header / div[1] / div / span[2] / a'
date_xpath = '//*[@id="documentContent"]/div[2]/div/header/div[2]/div[1]/span'
author_xpath = '//*[@id="documentContent"]/div[2]/div/header/div[2]/div[3]/div/div/span[1]/a'
search_term = "Three waters"


def main():
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(), options=options)
    url = create_url(URL, search_term)
    driver.get(url)
    more_buttons = driver.find_elements(By.XPATH, RNZ_BUTTON_XPATH)
    articles = get_url_and_text(driver)
    while more_buttons[0].is_displayed() and more_buttons[0].get_attribute('href') is not None:
        more_buttons[0].click()
        more_buttons = driver.find_elements(By.XPATH, RNZ_BUTTON_XPATH)
        articles.extend(get_url_and_text(driver))
    for article in articles:
        print(article.url)
        driver.get(article.url)
        article.article_type1 = get_element(driver, type_one_xpath)
        article.article_type2 = get_element(driver, type_two_xpath)
        article.date = get_element(driver, date_xpath)
        article.author = get_element(driver, author_xpath)
        if article.author is not None:
            article.author_url = driver.find_elements(By.XPATH, author_xpath)[0].get_attribute("href")
        try:
            article__body = BeautifulSoup(driver.page_source, 'html.parser').find("div", {"class": "article__body"})
            article.text = article__body.get_text()
        except:
            print("not processing")
    driver.close()





if __name__ == "__main__":
    main()
