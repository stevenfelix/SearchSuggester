#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 15:42:56 2018

@author: stevenfelix
"""

from nltk.tokenize import RegexpTokenizer # tokenizing
from nltk.corpus import stopwords  # list of stop words
from nltk.stem.wordnet import WordNetLemmatizer # lemmatizer
from itertools import product
import re



# %% Clean txt

## https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/deepir.ipynb

tokenizer = RegexpTokenizer(r'\w+') # tokens separated by white spice
stops = set(stopwords.words('english')) # list of english stop words
lemma = WordNetLemmatizer()

contractions = re.compile(r"'|-|\"")
# all non alphanumeric
symbols = re.compile(r'(\W+)', re.U)
# single character removal
singles = re.compile(r'(\s\S\s)', re.I|re.U)
# separators (any whitespace)
seps = re.compile(r'\s+')
# tokenizer
tokenizer = RegexpTokenizer(r'\w+') # tokens separated by white spice
# stop words
stops = set(stopwords.words('english')) # list of english stop words

# cleaner (order matters)
def clean(text, rmv_stop_words=True, return_tokens=False): 
    text = text.lower()
    text = contractions.sub('', text)
    text = symbols.sub(r' \1 ', text)
    text = singles.sub(' ', text)
    text = seps.sub(' ', text)
    tokens = tokenizer.tokenize(text)     # tokenize
    if rmv_stop_words:
        tokens = [i for i in tokens if not i in stops] # remove stop words
        text = ' '.join(tokens)
    if return_tokens:
        return tokens
    return text
    
# %%
""" These generate alternative queries and score them and filter them """

def generate_alternatives(query, n, model, rmv_stop_words=True, return_tokens=True, tags=[]):
    with open('input_queries.txt', 'a+') as f:
        f.write(query+'\n')
    syns = get_similar(query, model, rmv_stop_words=rmv_stop_words, return_tokens=return_tokens, tags=tags) # synonyms
    combs = get_combinations(syns) # combinations
    probs = [model.score([sug])[0] for sug in combs] # probabilities
    preds_probs =[(p,q) for p,q in zip(probs,combs)] # combine with queries
    preds_probs.sort(reverse=True)
    sugs =  [q for p,q in preds_probs[0:n]]
    return [' '.join(title) for title in sugs],syns

def get_similar(query, model, rmv_stop_words, return_tokens, tags, threshold=.55):
    q = clean(query, rmv_stop_words=rmv_stop_words, return_tokens=return_tokens)
    # turn each word  of query into its own list
    d = [[x] for x in q]
    for x in d:
        # for each word in original query, add topn similar words to list
        # TO DO: catch exceptions
        if x[0] not in tags:
            x.extend([syn for syn,score in model.most_similar(x[0]) if score > threshold])
    return d

def get_combinations(l):
    combs = [x for x in product(*l)]
    return combs