google taxonomy classifier demo
=========

An automatic Google Taxonomy Classifier built as a proof of concept for classification of Google product categorizers. The entire list of possible taxonomies can be found [here](http://www.google.com/basepages/producttype/taxonomy.en-US.txt). The demo contains three different components: scrape, train, test and eval.

**This is a proof of concept and not designed to work at scale or in production.**

Scrape
------

The scraping portion works by collecting data directly from Google's search. Using selenium categories are browsed and their descriptions stored. Sample dumps of the category descriptions for train and test are included as scraping product categories is currently very slow. Need to consider alternative scraping methods and alternate sources of product category data. To run the scraping portion:

    python taxonomy_demo.py -r scrape -d [NAME OF DUMP FILE] -c [FILE WITH LIST OF CATEGORIES]

Train
-----

After scraping you can now train a model on the data. Using out of the box models from scikit-learn you can train either a Naive Bayes model (-t nb) or Cosine Similarity (-t cosine). Train simply trains a model and saves a representation of the model to be loaded and used in test or eval.

    python taxonomy_demo.py -r train -d [NAME OF DUMP FILE] -t [MODEL TYPE: nb / cosine] -l [FILE TO SAVE MODEL]

Test
------

A quick way to interact with the model is included. Test provides a command line interace for playing with the model. Once you can immediately load it up and interact with it.

    python taxonomy.py -r test -l [MODEL FILE]

Eval
----

In the scrape method ~25% of the scraped descriptions are set aside as an evaluation set. Using scikit-learn's classification_report precision, recall, and f1 scores are computed for each category and averaged across all categories. To evalutate the model run

    python taxonomy.py -r eval -l [MODEL FILE] -e [EVAL FILE]

Sample Run
----------

Sample files have already been scraped and are included in the repo. Let's train a model on that data and interact with it.

    python taxonomy_demo.py -r train -t nb -d dump.p        # train model on the data
    python taxonomy_demo.py -r test                         # run test to interact


-------
License
-------

> The MIT License (MIT)

> Copyright (c) 2014 Bayes Consulting
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:

> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.
