import tweepy
import json
import sqlite3


consumer_key        = '<YOUR_CONSUMER_KEY>'
consumer_secret     = '<YOUR_CONSUMER_SECRET_KEY>'
access_token        = '<YOUR_ACCESS_TOKEN>'
access_token_secret = '<YOUR_ACCESS_TOKEN_SECRET>'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def createTweetsDB(db_name):
	conn = sqlite3.connect(db_name)
	c    = conn.cursor()
	c.execute('''
	          CREATE TABLE tweets
	          (id INTEGER PRIMARY KEY ASC, 
	          created_at varchar(250),
	          favorite_count INTEGER,
	          favorited INTEGER,
	          filter_level varchar(250),
	          lang varchar(250),
	          retweet_count INTEGER,
	          retweeted INTEGER,
	          source varchar(250),
	          text TEXT,
	          truncated INTEGER,
	          user_created_at varchar(250),
	          user_followers_count INTEGER,
	          user_location varchar(250),
	          user_lang varchar(250),
	          user_name varchar(250),
	          user_screen_name varchar(250),
			  user_time_zone varchar(250),
			  user_utc_offset INTEGER,
			  user_friends_count INTEGER)
	          ''')
	conn.commit()
	conn.close()


class MyStreamListener(tweepy.StreamListener):
	def on_status(self, status):
		print(status.text)

	def on_error(self, status):
		print(status)

	def on_data(self, data):
		all_data             = json.loads(data)
		created_at           = all_data['created_at']
		favorite_count       = all_data['favorite_count']
		favorited            = all_data['favorited']
		filter_level         = all_data['filter_level']
		lang                 = all_data['lang']
		retweet_count        = all_data['retweet_count']
		retweeted            = all_data['retweeted']
		source               = all_data['source']
		text                 = all_data['text']
		truncated            = all_data['truncated']
		user_created_at      = all_data['user']['created_at']
		user_followers_count = all_data['user']['followers_count']
		user_location        = all_data['user']['location']
		user_lang            = all_data['user']['lang']
		user_name            = all_data['user']['name']
		user_screen_name     = all_data['user']['screen_name']
		user_time_zone       = all_data['user']['time_zone']
		user_utc_offset      = all_data['user']['utc_offset']
		user_friends_count   = all_data['user']['friends_count']



		conn = sqlite3.connect('ffxv.db')
		c = conn.cursor()
		c.execute('''INSERT INTO tweets 
			(created_at, favorite_count, favorited, filter_level, lang, retweet_count, retweeted, source, text, truncated, user_created_at, user_followers_count, user_location, user_lang, user_name, user_screen_name, user_time_zone, user_utc_offset, user_friends_count) 
			VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', 
			(created_at, favorite_count, favorited, filter_level, lang, retweet_count, retweeted, source, text, truncated, user_created_at, user_followers_count, user_location, user_lang, user_name, user_screen_name, user_time_zone, user_utc_offset, user_friends_count))
		conn.commit()
		conn.close()



myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=['ffxv', 'ff xv', 'ff15', 'ff 15', 'final fantasy xv', 'final fantasy 15'])

createTweetsDB('ffxv.db')
