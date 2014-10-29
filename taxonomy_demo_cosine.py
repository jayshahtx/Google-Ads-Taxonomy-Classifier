#!/usr/bin/python2.7
"""First pass Google Taxonomy Classifier that trains on product categories
and classifies new product descriptions.

Categories to train on should be put in categories.txt and can be found in:
    http://www.google.com/basepages/producttype/taxonomy.en-US.txt

By: Matthew Ebeweber & Jay Shah
"""
import optparse
import pickle
import urllib
import sys
import dill
from random import random
from random import shuffle
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
import numpy
import pdb


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
    for element in elements[:39]:
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

    # print "{0}: {1}".format(category.encode('utf-8'), category_description.encode('utf-8'))
    return category_description.encode('utf-8').lower()


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
    count_transformer = CountVectorizer(stop_words='english')
    x_counts = count_transformer.fit_transform(x)

    tfidf_transformer = TfidfTransformer()
    x_tfidf = tfidf_transformer.fit_transform(x_counts)

    # Create a function that will appropriately transform a single input
    # to be classified by the trained classifier
    input_transform_fnc = lambda x: (
        tfidf_transformer.transform(count_transformer.transform([x]))
    )

    return (x_tfidf, input_transform_fnc)


def get_cmdline_opts_args():
    """ Handles the setting up of command line arguments and parsing them
    using optparse

    :rtype: (options, args)
    :returns: the parse options and args
    """
    # Parse the arguments for the flow
    parser = optparse.OptionParser()
    parser.add_option(
        '-t', '--type', dest='run_type',
        help='type of run: either scrape or train.'
    )
    # Scrape related arguments
    parser.add_option('-c', '--category_file', dest='category_file',
        default='categories.txt',
        help='scrape: filepath of list of categories'
    )
    parser.add_option('-d', '--dest', dest='pickle_dump_file',
        default='dump.p',
        help='scrape: filepath to pickle dump categories'
    )
    # Train & predict related arguments
    parser.add_option('-s', '--source', dest='pickle_source_file',
        default='dump.p', 
        help='train: name of file to load data'
    )
    # Classifier selection related arguments
    parser.add_option('-l', '--classifier', dest='class_source_file',
        default='class.p', 
        help="class: name of classifier to load")
    # Transformation function related arguments
    # Classifier selection arguments
    parser.add_option('-f', '--transformation_function', dest='transform_source_file',
        default='transform.p', 
        help="transformation function: function to transform arguments")

    return parser.parse_args()


if __name__ == "__main__":
    options, args = get_cmdline_opts_args()

    # Scrape workflow..
    if (options.run_type == 'scrape' or options.run_type == 'all'):
        # Read the categories from the file
        f = open('categories.txt', 'r')
        categories = [x.rstrip('\n') for x in f.readlines()]
        f.close()

        # Grab the category description for each category
        category_desc_pairs = [
            (category, category_desc_for(category))
            for category in categories
        ]

        # Dump these categories and descriptions to the file
        pickle.dump(
            category_desc_pairs,
            open(options.pickle_dump_file, 'w')
        )
    # Train and predict workflow..
    if (options.run_type == 'train' or options.run_type == 'all'):
        # Grab the categories and description arrays from the file
        # These serve as your (x, y) pairs
        cateogry_desc_pairs = pickle.load(
            open(options.pickle_source_file, 'r')
        )

        categories, category_descriptions = zip(*cateogry_desc_pairs)


        # convert all text into a document matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(category_descriptions)

        # get user input
        while True:
            user_input = raw_input("Enter text to classify: ")
            user_matrix = tfidf_vectorizer.transform([user_input])
            x = cosine_similarity(tfidf_matrix,user_matrix)
            index = numpy.where(x==max(x))[0][0]
            print categories[index]
            print


        ##############################################3











        categories, category_descriptions = zip(*cateogry_desc_pairs)

        # Transform the input data and get tranformation fnc
        (x, input_transform_fnc) = string_to_tfidf_input_transform(
            category_descriptions
        )

        # Get the NB classifier
        clf = train_naive_bayes_classifier(x, categories)

        # Write transformation function and classifier to disk
        dill.dump(
                input_transform_fnc, 
                open(options.transform_source_file, 'w')
        )
        pickle.dump(
                clf,
                open(options.class_source_file,'w')
        )

    # Jump straight to testing classification
    if (options.run_type == 'test' or options.run_type == 'all'):
        clf = pickle.load(
            open(options.class_source_file, 'r')
        )
        input_transform_fnc = dill.load(
            open(options.transform_source_file, 'r')
        )
        while True:
            user_input = raw_input("Enter text to classify: ")
            prediction = clf.predict(input_transform_fnc(user_input))
            print "Your prediction was: {0}".format(prediction)
    if ('scrape' or 'train' or 'test' or 'all' != options.run_type):
        sys.exit('Invalid Run Type: -t / --type must be scrape or train')
