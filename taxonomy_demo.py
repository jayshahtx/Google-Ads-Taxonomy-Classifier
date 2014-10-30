#!/usr/bin/python2.7
"""First pass Google Taxonomy Classifier that trains on product categories
and classifies new product descriptions.

Categories to train on should be put in categories.txt and can be found in:
    http://www.google.com/basepages/producttype/taxonomy.en-US.txt

By: Matthew Ebeweber & Jay Shah
"""
import optparse
import pickle
import sys
import dill

import google_shopping_scraper
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


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
    parser.add_option('-c', '--category_file', dest='categories_filename',
        default='categories.txt',
        help='scrape: filepath of list of categories'
    )
    parser.add_option('-d', '--dest', dest='pickle_dump_filename',
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


def scrape_workflow(categories_filename, dump_filename):
    """Helper function to define the scrape workflow. Reads in the categories,
    scrapes descriptions for the categories and dumps them to a file.

    :type categories_filename: String
    :param categories_filename: filepath to file containing categories
    :type dump_filename: String
    :param dump_filename: filepath to dump categories and category descriptions
    """
    # Read in the categories from categories_filename
    f = open(categories_filename, 'r')
    categories = [line.rstrip('\n') for line in f.readlines()]
    f.close()

    # Get the descriptions for each category
    cat_desc_pairs = google_shopping_scraper.get_catdesc_pairs_for_categories(
        categories
    )

    # Dump those pairs to the specified file
    pickle.dump(
        cat_desc_pairs,
        open(dump_filename, 'w')
    )


if __name__ == "__main__":
    options, args = get_cmdline_opts_args()

    # Scrape workflow.
    if options.run_type in ['scrape', 'all']:
        scrape_workflow(
            options.categories_filename, options.pickle_dump_filename
        )

    # Train workflow.
    if (options.run_type == 'train' or options.run_type == 'all'):
        # Grab the categories and description arrays from the file
        # These serve as your (x, y) pairs
        cateogry_desc_pairs = pickle.load(
            open(options.pickle_source_file, 'r')
        )

        categories, category_descriptions = zip(*cateogry_desc_pairs)


        # convert all text into a document matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(category_descriptions, stop_words = "english")

        # get user input
        while True:
            user_input = raw_input("Enter text to classify: ")
            user_matrix = tfidf_vectorizer.transform(user_input)
            cosine_similarity(tfidf_matrix,user_matrix)
            pdb.set_trace()


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
