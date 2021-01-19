#!/usr/bin/python3
#
# Webscraping Amazon products for their prices - used for buying items when prices are low.
#
# Maintainers: vo.ma@northeastern.edu


import sys
import csv
import sqlite3
from selenium import webdriver
from bs4 import BeautifulSoup

def get_url(search_term):
    """ Generate a URL string from a search term """
    template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_2'
    search_term = search_term.replace(' ', '+')

    # adding term query
    url = template.format(search_term)

    # adding page query
    url += '&page={}'

    return url

def extract_record(item):
    """ Extract and return data from a single record """
    result = None
    try:
        atag = item.h2.a
        description = atag.text.strip()
        url = 'https://www.amazon.com' + atag.get('href')
    except AttributeError as e:
        return

    try:
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
    except AttributeError as e:
        return

    try:
        rating = item.i.text
        review_count = item.find('span', {'class': 'a-size-base', 'dir': 'auto'}).text
    except AttributeError as e:
        rating = 0.0
        review_count = 0
        
    result = (description, price, rating, review_count, url)

    return result

def add_records_to_db(records):
        connection = sqlite3.connect('amazon.db')
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS apple_products")
        cursor.execute("CREATE TABLE IF NOT EXISTS apple_products (id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                                                                      "description TEXT, " +
                                                                      "price REAL, " +
                                                                      "rating REAL, " + 
                                                                      "review_count INTEGER, " +
                                                                      "url TEXT);")

        for record in records:
            # (description, price, rating, review_count, url)
            items = []
            items.append(record[0])
            price = record[1].split("$")
            price = float(price[1].replace(',', ''))
            items.append(price)
            rating = record[2]
            if rating != 0.0:
                rating = float(rating[0:3])
            items.append(rating)
            review_count = record[3]
            if record[3] != 0:
                review_count = (int(record[3].replace(',', '')))
            items.append(review_count)
            items.append(record[4])
            
            cursor.execute("INSERT INTO apple_products(description, price, rating, review_count, url) \
                                    VALUES (?, ?, ?, ?, ?)", tuple(items))
            connection.commit()

        print('All records inserted into DB')
        connection.close()

if __name__ == '__main__':
    products = ['macbook pro', 'apple watch', 'airpods pro', 'iphone 12', 'ipad pro']

    driver = webdriver.Chrome()

    records = []

    for product in products:
        url = get_url(product)
        # Extracting the collection, only going through 3 pages of results
        for page in range(1, 4):
            driver.get(url.format(page))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = soup.find_all('div', {'data-component-type': 's-search-result'})

            # Only pulling valid search results
            for item in results:
                record = extract_record(item)
                if record:
                    records.append(record)

        
    driver.close()  
    add_records_to_db(records)     
    sys.exit(0)