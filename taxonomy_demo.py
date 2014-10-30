#!/usr/bin/python2.7
"""First pass Google Taxonomy Classifier that trains on product categories
and classifies new product descriptions.

Categories to train on should be put in categories.txt and can be found in:
    http://www.google.com/basepages/producttype/taxonomy.en-US.txt

By: Matthew Ebeweber & Jay Shah
"""
import dill
import optparse
import cPickle as pickle
import sys

import classifier
import google_shopping_scraper


def get_cmdline_opts_args():
    """ Handles the setting up of command line arguments and parsing them
    using optparse

    :rtype: (options, args)
    :returns: the parse options and args
    """
    parser = optparse.OptionParser()

    # Type of run / workflows to do
    parser.add_option(
        '-r', '--run-type', dest='run_type',
        help='type of run: either scrape or train.'
    )

    # Filename of .txt file containing all of the categories
    parser.add_option('-c', '--category-file', dest='categories_filename',
        default='categories.txt',
        help='scrape: filepath of list of categories'
    )

    # Dump of the category information to save / load
    parser.add_option('-d', '--dest', dest='cateogry_desc_dump_filename',
        default='dump.p',
        help='scrape: filepath to pickle dump categories'
    )

    # Dump of the classifier to save / load
    parser.add_option('-l', '--clf-filename', dest='clf_filename',
        default='clf.p',
        help="class: filename of classifier to load")

    # Classifier type to run
    parser.add_option('-t', '--clf-type', dest='clf_type',
        help='clf-type: the classifier type to use'
    )

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


def classifier_workflow(training_data_loc, classifier_type, clf_dump_filename):
    """Helper function to train a classifier to classify. Reads in the (x, y)
    pairs, trains the appropriate classifier and saves the classifier.
    """
    # Read in the category description pairs
    cateogry_desc_pairs = pickle.load(
        open(training_data_loc, 'r')
    )

    # Train a classifier accordingly
    if classifier_type == 'nb':
        clf = classifier.MultinomialNBClassifier(
            cateogry_desc_pairs
        )
    elif classifier_type == 'cosine':
        clf = classifier.CosineClassifier(
            cateogry_desc_pairs
        )
    else:
        exit('invalid classifier type')

    # Save the new trained classifier
    dill.dump(
        clf,
        open(clf_dump_filename, 'w')
    )


def test_workflow(clf_filename):
    """Helper function to test a classifier interactively. Takes in a file
    where a given Classifier is stored. Loads the classfier up and prompts for
    queries
    """
    clf = dill.load(open(clf_filename, 'r'))

    while True:
        user_input = raw_input('Enter text to classify (q to quit): ')
        if user_input == 'q': break

        prediction = clf.classify(user_input.lower())
        print 'Prediction: {0}'.format(prediction)


if __name__ == "__main__":
    options, args = get_cmdline_opts_args()

    # Scrape workflow.
    if options.run_type in ['scrape', 'all']:
        scrape_workflow(
            categories_filename=options.categories_filename,
            dump_filename=options.cateogry_desc_dump_filename
        )

    # Train workflow.
    if options.run_type in ['train', 'all']:
        classifier_workflow(
            training_data_loc=options.cateogry_desc_dump_filename,
            classifier_type=options.clf_type,
            clf_dump_filename=options.clf_filename
        )

    # Test workflow.
    if options.run_type in ['test', 'all']:
        test_workflow(
            clf_filename=options.clf_filename
        )

    # Invalid RunType.
    if options.run_type not in ['scrape', 'train', 'test', 'all']:
        sys.exit('-r / --run-type must be scrape, train, test or all')
