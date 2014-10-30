#!/usr/bin/python2.7
"""google_shopping_scraper.py

Handles the scraping portion for the Google Product Taxonomy classifier.
"""
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

    category_description = ""
    google_shopping_base = 'https://www.google.com/search?'
    parameters = urllib.urlencode({
        'tbm': 'shop',  # pull google shopping
        'q': category,
        'oq': category
    })
    url = google_shopping_base + parameters

    # Google's shopping pages load information through javascript
    # so we need something to actually load the page before grabbing
    # the source
    driver = webdriver.Firefox()  # need to use real browser
    driver.get(url)

    # Grab all of the elements to click and shuffle them
    elements = driver.find_elements_by_class_name('psgiimg')
    shuffle(elements)

    # Go through each, expand and pull the text
    for element in elements[:3]:
        element.click()

        # Sleep randomly to let load
        sleep(random() * 2)

        # Pull the source from the page
        soup_html = BeautifulSoup(driver.page_source)

        try:
            category_description += (
                soup_html.find('span', class_="pspo-fdesc-txt").text + " "
            )
        except AttributeError:
            print("Failed to find element")


    # Kill the selenium browser
    driver.close()

    return category_description.encode('utf-8').lower()


def get_catdesc_pairs_for_categories(categories):
    """Takes a list of categories and returns a mapping of those categories to
    their product descriptions

    :type categories: Array(String)
    :param categories: categories to retrieve description for
    :rtype: (String, String)
    :returns: list of categories and their corresponding descriptions
    """
    return [
        (category, category_desc_for(category))
        for category in categories
    ]
