import tweepy
import json
import sqlite3
import re 
from collections import defaultdict
from itertools import groupby
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import numpy as np
import requests
from wordcloud import WordCloud


def plotTweetByLang(db_name):
	conn = sqlite3.connect(db_name)
	c = conn.cursor()

	c.execute("SELECT user_lang, COUNT(user_lang) FROM tweets GROUP BY user_lang HAVING COUNT(user_lang)>20 ORDER BY COUNT(user_lang) DESC")

	langs = []
	langs_count = []

	for lang, lang_count in c.fetchall():
		langs.append(lang)
		langs_count.append(lang_count)

	# Plot lang
	x = [i for i in range(len(langs))]
	plt.bar(x, langs_count)
	plt.xticks(x, langs)
	plt.xlabel("User language")
	plt.ylabel("Number of tweets associated with the language \n (total 12 389 tweets)")
	plt.show()

	conn.close()

def cleanTweetText(tweet):
	retweet_rx = re.compile(r'RT @\w+:\s') 
	url_rx     = re.compile(r'https://\w\.\w+/\w+')
	hashtag_rx = re.compile(r'#\w+\s')
	to_user_rx = re.compile(r'@\w+\s')
	regex      = [retweet_rx, url_rx, hashtag_rx, to_user_rx]
	for rx in regex:
		tweet = re.sub(rx, '', tweet)
	return tweet

def getTweetFromDB(db_name, lang, nb_tweets):
	conn = sqlite3.connect(db_name)
	c = conn.cursor()
	c.execute("SELECT text FROM tweets WHERE lang=? LIMIT ?", (lang, nb_tweets))
	for tweet in c.fetchall():
		yield tweet

def getHashtag(tweet):
	# return list of hashtags
	hashtag_rx = re.compile(r'#\w+')
	hashtags = hashtag_rx.findall(tweet)
	return hashtags

def countHashtag(hashtags_list):
	# return a dict hashtag/frequency pair
	hashtags_freq = defaultdict( int )
	for h in hashtags_list:
		hashtags_freq[h.lower()] += 1 
	return dict(hashtags_freq)

def createWordCloud(all_words_list):
	wordcloud = WordCloud(font_path='C:\Windows\Fonts\AozoraMinchoBlack.ttf', width = 1000, height = 500).generate(' '.join(all_words_list))
	plt.figure(figsize=(15,8))
	plt.imshow(wordcloud)
	plt.axis("off")
	plt.show()

def getAllHashtags(all_tweets):
	all_hashtags = []
	for tweet in all_tweets:
		hashtags_list = getHashtag(tweet[0])
		all_hashtags.extend([h for h in hashtags_list])
	return all_hashtags

def printMostFrequentHashtags(nb_most_hashtagged, all_hashtags):
	hTag_freq_dict = countHashtag(all_hashtags)
	most_Htag_values = sorted(list(hTag_freq_dict.values()), reverse=True)[:nb_most_hashtagged]
	for i in most_Htag_values:
		print (list(hTag_freq_dict.keys())[list(hTag_freq_dict.values()).index(i)])


def getTweetSentiment(all_tweets):
	for tweet in all_tweets:
		cleaned_tweet = cleanTweetText(tweet[0])
		tweet_sentiment = TextBlob(cleaned_tweet).sentiment
		yield tweet_sentiment

def plotSentiment():
	polarity = []
	subjectivity = []
	for sentiment in getTweetSentiment(all_tweets):
		polarity.append(sentiment.polarity)
		subjectivity.append(sentiment.subjectivity)

	plt.scatter(polarity, subjectivity, c=polarity, s=100, cmap='RdYlGn')
	plt.xlabel('Tweet polarity')
	plt.ylabel('Tweet subjectivity')
	plt.xlim(-1.1, 1.1)
	plt.ylim(-0.1, 1.1)
	plt.show()

	positive_polarity = [p for p in polarity if p>0]
	negative_polarity = [n for n in polarity if n<0]
	neutral_polarity = [r for r in polarity if r==0]

	total_size = len(positive_polarity) + len(negative_polarity) + len(neutral_polarity)
	n_size = len(negative_polarity)/total_size
	p_size = len(positive_polarity)/total_size
	r_size = len(neutral_polarity)/total_size

	labels = ['Neutral tweets', 'Positive tweets', 'Negative tweets']
	sizes = [r_size, p_size, n_size]
	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
	        shadow=True, startangle=90)
	ax1.axis('equal')
	plt.show()

def plotMostUsedWordsCloud(all_tweets):
	stop_words = set(stopwords.words('english'))
	all_tweets_words = []
	for tweet in all_tweets:
		cleaned_tweet = cleanTweetText(tweet[0])
		tweet_word_token = word_tokenize(cleaned_tweet)
		tweet_word_token = [w.lower() for w in tweet_word_token if w not in [stop_words, 'rt', 'https'] ]
		all_tweets_words.extend(tweet_word_token)
	createWordCloud(all_tweets_words)


if __name__ == '__main__':
	db_name = 'twitter.db'
	all_tweets = getTweetFromDB(db_name, 'en', 7000)

	plotTweetByLang(db_name)
	all_hashtags = getAllHashtags(all_tweets)
	printMostFrequentHashtags(15, all_hashtags)
	createWordCloud(all_hashtags)
	plotSentiment()
	plotMostUsedWordsCloud(all_tweets)