#!/usr/bin/python2.7
"""First pass Google Taxonomy Classifier that trains on product categories
and classifies new product descriptions.

By: Matthew Ebeweber & Jay Shah
"""
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
    # TODO(matthewe|2014-10-25): Currently these are hardcoded. This will
    # be moved to scrape Google Products and construct the text about
    # the product category.
    if "Basketball Shoes" == category:
        return (
            "2014 hot sale lebron 11 men and women basketball shoes "
            "sports shoes sneakers high quality champion edition shoes Free "
            "shipping Stay cool under pressure while you wear the Under Armour "
            "Men's ClutchFit Lightning basketball shoe. Lightweight, "
            "engineered upper materials promote a comfortable fit by "
            "throughout your moves. Execute the assist as the external "
            "full-length Micro G midsole acts as a soft and stable platform "
            "to absorb impact, setting you up for your next move. A "
            "multidirectional traction pattern keeps you in control "
            "throughout the game."
        )
    elif "Running Shoes" == category:
        return (
            "The Nike Air Pegasus '89 Mens Running Shoes are a classic "
            "brought back to life. A blast from the past, these are sure to "
            "turn heads whether on a jog or wearing casually Designed for "
            "the runner who wants bold midfoot support and a resilient ride, "
            "our breathable Nike Reax Run 8 shoes will keep him on track to "
            "the finish line. Engage your run from start to finish with the "
            "cushioned landings and explosive takeoffs"
        )
    elif "Soccer Cleats" == category:
        return (
            "Perform like a champion every game in the Mercurial Vortex. "
            " A soft trophy synthetic leather upper with sculpted last ensures "
            "unmatched ball touch, durability and fit. The adidas Men's 11nova1 "
            "TRX FG Soccer Cleats feature free-kick leather uppers and TRAXION "
            "outsoles. Nike Yellow Tiempo Genio Men's Leather FG Soccer Cleats"
        )


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
