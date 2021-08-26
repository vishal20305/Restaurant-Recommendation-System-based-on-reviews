# -*- coding: utf-8 -*-

import pandas as pd
import nltk
#nltk.download('stopwords')
#nltk.download('punkt')
import re
import sys
import json
import pickle
import os.path
import math
import numpy as np
from numpy.linalg import norm
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from fuzzywuzzy import fuzz

data = pd.read_csv('zomato.csv')
#data.head()
#pd.set_option('display.max_colwidth', None)
#data.reviews_list[0]

#print(len(data))
data = data[data.reviews_list != '[]']
data = data.reset_index(drop=True)
#print(len(data))
#data[50:100]

def preprocess_name(name):
  name = name.replace('\x82', '')
  name = name.replace('\x83', '')
  return name


combined_reviews = {}
for index, row in data.iterrows():
  res = row['name'].strip() + '_' + row['location'].strip()
  if res not in combined_reviews:
    combined_reviews[res] = {'name' : preprocess_name(row['name']), 'address' : row['address'],
      'rate': str(row['rate']) , 'phone' : str(row['phone']), 'location' : row['location'],
      'cuisines' : row['cuisines'], 'reviews_list' : row['reviews_list']
    }
  else:
    combined_reviews[res]['reviews_list'] += (' ' + row['reviews_list'])

location = sys.argv[3].strip()
#location = "Banasank"

if location != "":
  filtered_res = {}
  for id, res in combined_reviews.items():
    if fuzz.ratio(res['location'], location) > 40:
      filtered_res[id] = res
  combined_reviews = filtered_res

name  = sys.argv[1].strip()
#name = "cafe"

if name != "":
  filtered_res = {}
  for id, res in combined_reviews.items():
    #print(f"{res['name']} {name}")
    if fuzz.ratio(res['name'], name) > 60:
      filtered_res[id] = res
  combined_reviews = filtered_res

filtered = False
if name!="" or location!="":
  filtered = True

#print(combined_reviews.keys())

data = {}
i = 1
for k, v in combined_reviews.items():
  data[i] = v
  i += 1
#print(combined_reviews)
#print(len(data))

"""
  Vishal -> Preprocessing
"""

def preprocess(doc):
    doc = doc.replace('x82', ' ')
    doc = doc.replace('x83', ' ')
    doc = doc.replace('RATED\\n', '')
    doc = doc.replace('\\n', ' ')
    doc = re.sub(r'Rated \d.0', '', doc)
    doc = re.sub(r'[^a-zA-Z/\s]','', doc)
    doc = doc.lower()
    #print(doc)
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(doc)
    doc_without_stop_words = [w for w in word_tokens if not w in stop_words]

    return doc_without_stop_words

"""
  Aishwariya -> Bag of Words
"""

# initialize empty dictionary for name of restaurants (document name)
if not filtered and os.path.isfile('restaurants.pkl'):
  temp = open("restaurants.pkl", "rb")
  restaurants = pickle.load(temp)
  restaurants_loaded = True
else:
  restaurants = {}
  restaurants_loaded = False
# initialize empty dictionary for restaurant reviews (documents)
if not filtered and os.path.isfile('reviews.pkl'):
  temp = open("reviews.pkl", "rb")
  reviews = pickle.load(temp)
  reviews_loaded = True
else:
  reviews = {}
  reviews_loaded = False
# bag of words conytaining terms from query and documents
bag_of_words = []
# number of doc to be traversed
N = int(len(data)) # roughly 2K docs
# map restaurant names and reviews against restaurant id
for i in range(N):
  if not restaurants_loaded:
    restaurants[i+1] = {'name' : data[i+1]['name'], 'address' : data[i+1]['address'], 'rating' : data[i+1]['rate'],
      'phone' : data[i+1]['phone']
    }
  # restaurants[i+1] = preprocess(restaurants[i+1])
  if not reviews_loaded:
    reviews[i+1] = preprocess(data[i+1]['reviews_list'])
  # store all terms in bag of words
  bag_of_words += reviews[i+1]

if not filtered:
  if os.path.isfile('restaurants.pkl'):
    pass
  else:
    restaurants_file = open("restaurants.pkl", "wb")
    pickle.dump(restaurants, restaurants_file)
    restaurants_file.close()

if not filtered:
  if os.path.isfile('reviews.pkl'):
    pass
  else:
    reviews_file = open("reviews.pkl", "wb")
    pickle.dump(reviews, reviews_file)
    reviews_file.close()

def input_query(q = ""):
  if q == "":
    return input()
  else:
    return q

query = input_query(sys.argv[2].strip())

preprocessed_query = preprocess(query)
bag_of_words += preprocessed_query
bag_of_words = list(set(bag_of_words))

def create_query_vector(query):
  #global bag_of_words
  #query_vector = dict.fromkeys(bag_of_words, 0)
  query_vector = {}
  for word in query:
    if word not in query_vector:
      query_vector[word] = 1
    else:
      query_vector[word] += 1
  return query_vector

query_vector = create_query_vector(preprocessed_query)
#print(query_vector)

def create_doc_vectors(reviews):
  if not filtered and os.path.isfile('docs.pkl'):
    temp = open("docs.pkl", "rb")
    doc_vectors = pickle.load(temp)

  else:
    doc_vectors = {}
    for id, review in reviews.items():
      doc_vectors[id] = {}
      for word in review:
        if word not in doc_vectors[id]:
          doc_vectors[id][word] = 1
        else:
          doc_vectors[id][word] += 1
  return doc_vectors

doc_vectors = create_doc_vectors(reviews)

if not filtered:
  if os.path.isfile('docs.pkl'):
    pass
  else:
    doc_vectors_file = open("docs.pkl", "wb")
    pickle.dump(doc_vectors, doc_vectors_file)
    doc_vectors_file.close()

#ranking according TF IDF scoring scheme

tf = {}
df = {}
for term in preprocessed_query:
  tf[term] = {}
  df[term] = 0
  for id, doc in doc_vectors.items():
    tf[term][id] = 0
    if term in doc:
      tf[term][id] = doc[term] / len(doc)
      df[term] += 1

#print(tf['hygiene'][2])
#print(df['hygiene'])
idf = {}
N = len(doc_vectors)
for term in preprocessed_query:
  idf[term] = math.log10(N/(df[term]+0.1))

#print(idf['good'])

tfidf = {}
for id, doc in doc_vectors.items():
  tfidf[id] = {}
  for term in preprocessed_query:
    tfidf[id][term] = tf[term][id] * idf[term]

tfidf_scores = {}
for key, val in tfidf.items():
  tfidf_scores[key] = sum(tfidf[key].values())

tfidf_scores = sorted(tfidf_scores.items(), key=lambda item: item[1], reverse=True)
tfidf_scores = {k: v for k, v in tfidf_scores}
#print(tfidf_scores)
top_50 = list(tfidf_scores.keys())[:50]
result = {}
i=1
for doc in top_50:
  result[i] = restaurants[doc]
  i += 1
#print(json.dumps(result))

"""OVER"""

def document_length(doc_vectors):
  total_length = 0
  for id, doc in doc_vectors.items():
    total_length += len(doc)
  return total_length/len(doc_vectors)

"""**Probabilistic  Model**"""

def bm25_score(doc_vectors, query):
  scores = {}
  k1 = 1.5
  b = 0.75
  avg_doc_length = document_length(doc_vectors)
  for id, doc in doc_vectors.items():
    score_of_document = 0
    for term in query:
      numerator = idf[term] * tf[term][id] * (k1+1)
      denominator = tf[term][id] + k1*(1 - b + (b*(len(doc)/avg_doc_length)))
      score_of_document += numerator/denominator
    scores[id] = score_of_document
  return scores

bm25_scores = bm25_score(doc_vectors, preprocessed_query)
bm25_scores = sorted(bm25_scores.items(), key=lambda item: item[1], reverse=True)
bm25_scores = {k: v for k, v in bm25_scores}
#print(bm25_scores)
top_50 = list(bm25_scores.keys())[:50]
result = {}
i=1
for doc in top_50:
  result[i] = restaurants[doc]
  i += 1
  #print(restaurants[doc])

print(json.dumps(result))
