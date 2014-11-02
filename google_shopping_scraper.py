#!/usr/bin/python2.7
"""google_shopping_scraper.py

Handles the scraping portion for the Google Product Taxonomy classifier.
"""
import os
import urllib
from random import random
from random import shuffle
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver


def category_desc_for(category):
    """Takes a category and returns text assoiated with that category after
    searching Google Products and other sources.

    :type category: string
    :param category: category to scrape information for

    :rtype: string
    :returns: space separated text related to that cateogry
    """
    print "Gathering descriptions for: {0}".format(category)

    google_shopping_base = 'https://www.google.com/search?'
    parameters = urllib.urlencode({
        'tbm': 'shop',  # pull google shopping
        'q': category,
        'oq': category,
        'tbs': 'vw:g'
    })
    url = google_shopping_base + parameters

    # Google's shopping pages load information through javascript
    # so we need something to actually load the page before grabbing
    # the source
    # TODO(matthewe): evaluate using Chrome for speed
    driver = webdriver.Firefox()        # need to use real browser
    driver.get(url)

    # Collect 40 different descriptions
    descriptions = []

    last = ""
    pages = 0
    while len(descriptions) < 20:
        # Grab all of the elements to click and shuffle them
        driver.implicitly_wait(5)
        sleep(2 * random())
        elements = driver.find_elements_by_class_name('psgiimg')
        shuffle(elements)

        # TODO(matthewe|2014-10-30): scraping could use some work, doesn't
        # always find decription.
        desc_count = 0
        for element in elements:
            if desc_count < 3:
                element.click()
                try:
                    # Pull the source from the page
                    sleep(2 * random())
                    soup_html = BeautifulSoup(driver.page_source)
                    desc = soup_html.find('span', class_="pspo-fdesc-txt").text

                    # TODO(matthewe|2014-10-30): exploring using selenium to scrape
                    # sleep(2)
                    # more_button = driver.find_elements_by_class_name('pspo-togdesc')
                    # if more_button and more_button.is_displayed():
                    #     driver.find_elements_by_class_name('pspo-togdesc')[0].click()
                    # sleep(2)
                    # desc = driver.find_elements_by_class_name('pspo-fdesc-txt')[-1].text
                    if desc.strip() and desc != last:
                        descriptions.append(desc)
                        last = desc
                        desc_count += 1
                except AttributeError:
                    print("Failed to find element")

        driver.find_elements_by_id('pnnext')[0].click()
        pages += 1
        driver.implicitly_wait(10)

    # Kill the selenium browser
    driver.close()

    # Split into train and test data
    cutoff = int(len(descriptions) * .75)
    return (
        descriptions[:cutoff],
        descriptions[cutoff:]
    )


def get_catdesc_pairs_for_categories(categories):
    """Takes a list of categories and returns a mapping of those categories to
    their product descriptions

    :type categories: Array(String)
    :param categories: categories to retrieve description for
    """
    catdesc_pairs = []
    eval_list_pairs = []
    for category in categories:
        train_category_desc, eval_list = category_desc_for(category)

        catdesc_pairs.append(
            (category, ' '.join(train_category_desc))
        )

        eval_list_pairs.append(
            (category, eval_list)
        )

    return dict(
        catdesc_pairs=catdesc_pairs,
        eval_list_pairs=eval_list_pairs
    )
