"""Defines an abstract classifier and individual classifiers to be used.

By: Jay Shah and Matt Ebeweber
"""
import abc

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


class Classifier(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def train(self, xy_pairs):
        """Trains a classifier based on the xy pairs."""
        raise NotImplementedError

    @abc.abstractmethod
    def classify(self, x):
        """Classifies a single instance"""
        raise NotImplementedError


class MultinomialNBClassifier(Classifier):
    """A classifier backed by sci-kit learns MultinomialNB"""

    def __init__(self, xy_pairs):
        """Takes xy_pairs and trains a classifier"""
        self.clf, self.transform_fnc = self.train(xy_pairs)

    def train(self, xy_pairs):
        """Trains a classifier based on the x, y pairs. Returns the trained
        classifier and the input transformation"""
        y, x = zip(*xy_pairs)

        count_transformer = CountVectorizer(stop_words='english')
        x_counts = count_transformer.fit_transform(x)

        tfidf_transformer = TfidfTransformer()
        x_tfidf = tfidf_transformer.fit_transform(x_counts)

        input_transform_fnc = lambda x: (
            tfidf_transformer.transform(count_transformer.transform([x]))
        )

        clf = MultinomialNB()
        clf.fit(x_tfidf, y)

        return (clf, input_transform_fnc)

    def classify(self, x):
        """Transforms and classifies x"""
        return self.clf.predict(
            self.transform_fnc(x)
        )
