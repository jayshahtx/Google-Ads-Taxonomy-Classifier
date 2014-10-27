#!/usr/bin/python2.7
"""First pass Google Taxonomy Classifier that trains on product categories
and classifies new product descriptions.

By: Matthew Ebeweber & Jay Shah
"""
import urllib
from random import random
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

# Categories we will train on. These should match Google's Taxonomy:
# http://www.google.com/basepages/producttype/taxonomy.en-US.txt
product_categories = [
    "Basketball Shoes",
    "Running Shoes",
    "Soccer Cleats"
]


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
    elements = driver.find_elements_by_class_name('psgiimg')

    # Go through each, expand and pull the text
    for element in elements[:3]:
        element.click()

        # Sleep randomly to let load
        sleep(random() * 2)

        # Pull the source from the page
        soup_html = BeautifulSoup(driver.page_source)

        category_description += (
            soup_html.find('span', class_="pspo-fdesc-txt").text + " "
        )


    # Kill the selenium browser
    driver.close()

    print "{0}: {1}".format(category, category_description)
    return category_description


def train_naive_bayes_classifier(x, y):
    """Trains a Naive Bayes MultinomialNB classifier after perprocessing x.

    :type x: [String, String, ...]
    :param x: an array of product descriptions
    :type y: [String, String, ...]
    :param y: categories mapping to each x

    :rtype: (fnc, Classifier)
    :returns: a function to transform a new input and a Classfier
    """
    return MultinomialNB().fit(x, y)


def string_to_tfidf_input_transform(x):
    """Tranforms the input into a format that will be used to train the
    classifier. Returns the transformed input and a function to transform
    future inputs.

    :type x: [String, String, ...]
    :param x: Array of Strings to be transformed

    :rtype: (transformed_input, fnc)
    :returns:
        the transformed input and a function to transform future inputs
    """
    count_transformer = CountVectorizer()
    x_counts = count_transformer.fit_transform(x)

    tfidf_transformer = TfidfTransformer()
    x_tfidf = tfidf_transformer.fit_transform(x_counts)

    # Create a function that will appropriately transform a single input
    # to be classified by the trained classifier
    input_transform_fnc = lambda x: (
        tfidf_transformer.transform(count_transformer.transform([x]))
    )

    return (x_tfidf, input_transform_fnc)


if __name__ == "__main__":
    # Get descriptions for each category to train on
    product_category_descriptions = [
        category_desc_for(category)
        for category in product_categories
    ]

    # Transform the input data and get tranformation fnc
    (x, input_transform_fnc) = string_to_tfidf_input_transform(
        product_category_descriptions
    )

    # Get the NB classifier
    clf = train_naive_bayes_classifier(x, product_categories)

    # Prompt user for input and classify
    user_input = raw_input("Enter text to classify: ")
    prediction = clf.predict(input_transform_fnc(user_input))
    print "Your prediction was: {0}".format(prediction)
