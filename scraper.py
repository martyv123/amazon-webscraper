#!/usr/bin/python3
#
# Webscraping Amazon products for their prices - used for buying items when prices are low.
#
# Maintainers: vo.ma@northeastern.edu

# TODO: have results sent to email, and stored in database

import csv
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()

def get_url(search_term):
    """ Generate a URL string from a search term """
    template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_2'
    search_term = search_term.replace(' ', '+')
    return template.format(search_term)

if __name__ == '__main__':
    url = get_url('ultrawide monitor')

    driver.get(url)