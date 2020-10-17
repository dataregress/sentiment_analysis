
# Credit to Huxley for infinite scroll page parsing
# Original: https://dev.to/mr_h/python-selenium-infinite-scrolling-3o12

# importing whats needed
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import datetime as dt
import os
from os import path


def get_news(company_ticker, number_of_news):

    # initializing the web driver
    options = webdriver.ChromeOptions()

    # change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(
        executable_path="F:\\Projects\\Stocks_Sentiments\\selenium_driver\\chromedriver.exe",
        options=options)
    driver.set_window_size(1120, 1000)

    # base url to start from. you can change parameters by opening the below url in browser
    # and then modify the onscreen filters, and then copy-paste the updated url below
    url = 'https://wallmine.com/screener?d=d&nd=93&r=n&s=' + company_ticker

    driver.get(url)

    df_column_names = ['id', 'symbol', 'headline', 'summary', 'date_time']

    all_news = []
    news_id = 1
    # looping until the number of property
    while len(all_news) < number_of_news:
        time.sleep(25)

        news_rows = driver.find_elements_by_class_name("js-clickable-row")

        for news_row in news_rows:

            time.sleep(1)

            try:
                news_soup = BeautifulSoup(news_row.get_attribute('innerHTML'), 'html.parser')

                if len(all_news) >= number_of_news:
                    break

                # getting the list of all anchor tags for property details page
                news_tooltip = news_soup.find('td', {'class': 'js-tooltip'})

                if news_tooltip is not None:
                    news_headline = news_tooltip.find('a').text

                    if len(news_tooltip.attrs) > 0:
                        raw_tooltip_data = news_tooltip.attrs['data-original-title']
                        raw_tooltip_data.replace('<br />', '|')
                        raw_tooltip_data = clean_html(raw_tooltip_data)

                        news_date = raw_tooltip_data.split('\n\n')[0]
                        news_date = news_date[0:news_date.rfind('-')]
                        news_date = news_date.replace('T', ' ')
                        news_date = dt.datetime.strptime(news_date, '%Y-%m-%d %H:%M:%S')

                        news_summary = raw_tooltip_data.split('\n\n')[1]

                        if len(news_summary) < 50:
                            continue

                news = {'id': news_id,
                        'symbol': company_ticker,
                        'headline': news_headline,
                        'summary': news_summary,
                        'date_time': news_date}

                all_news.append(news)
                news_id += 1
                print("Scrapping news {} of {}.".format(len(all_news), number_of_news))
            except:
                continue

        if len(all_news) < number_of_news:
            next_button = driver.find_element_by_xpath(".//li[@class='page-item next-page']/a[@rel='next']").click()

            if next_button is not None:
                next_button.click()

    df_all_news = pd.DataFrame(all_news)
    save_data_csv(df_all_news, 'all_news.csv')


def save_data_csv(data_frame, filename):

    # checking if the file exist. delete if it is already there
    if path.exists(filename):
        os.remove(filename)

    # saving to csv. please include .csv extension in filename
    data_frame.to_csv(filename, index=False)


def clean_html(raw_html):
    clean_re = re.compile('<.*?>')
    clean_text = re.sub(clean_re, '', raw_html)

    return clean_text
