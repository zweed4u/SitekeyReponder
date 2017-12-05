#!/usr/bin/python3.6

import json
import tweepy
import requests
import datetime
from tweepy import Stream
from bs4 import BeautifulSoup
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import signal
import sys


class StdOutListener(StreamListener):
	def __init__(self, DEBUG=False):
		self.DEBUG = DEBUG
		self.tweetCount = 0

	def on_connect(self):
		print("Connection established!!\n========================")

	def on_disconnect(self, notice):
		print("Connection lost!! : ", notice)

	def on_data(self, status):
		global url, response
		status = json.loads(str(status))
		if self.DEBUG:
			print(status)
		if 'text' in status.keys():  # this is a tweet
			if status['text'].split()[0] == '@SiteKeyFetch':  # make sure the tweet is a mention
				if len(status['entities']['urls']):  # entities key has urls
					self.tweet_text = status['text']
					self.tweeters_name = status['user']['screen_name']
					self.tweeters_id = status['user']['id_str']
					self.link_to_tweet = f'https://twitter.com/{self.tweeters_name}/status/{status["id_str"]}'
					#url = self.tweet_text.split()[1]  # tweets format must contain link as next 'word' after '@''
					url = status['entities']['urls'][0]['expanded_url'] # Dont know if this index changes... must be for when there are multiple links in 1 tweet. only accept and take 1st url
					url = url.replace('\\', '') # unescape backslashes
					if self.DEBUG:
						print(url)
					self.site_key = self.fetch_site_key(url)  # need to sanitize/check this
					print(f'{datetime.datetime.now()} :: Tweeting {self.site_key} to {self.tweeters_name}')
					api.update_status(f'@{self.tweeters_name} {self.site_key}', in_reply_to_status_id=status['id_str'])
					self.tweetCount += 1  # increment tweet count

	def fetch_site_key(self, url):
		session = requests.session()
		response = session.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'})
		soup = BeautifulSoup(response.content, "html5lib")
		if self.DEBUG:
			print(response.content)
		return soup.findAll('div', {'class':'g-recaptcha'})[0]['data-sitekey']  # this is dependent on site's implementation of recaptcha must have it in a div with class name 'g-recaptcha' with the 'data-sitekey' attribute being the attribute of interest

	def on_error(self, status):
		#Verbose error code
		if status == 200:
			print(str(status)+' :: OK - Success!')
		elif status == 304:
			print(str(status)+' :: Not modified')
		elif status == 400:
			print(str(status)+' :: Bad request')
		elif status == 401:
			print(str(status)+' :: Unauthorized')
		elif status == 403:
			print(str(status)+' :: Forbidden')
		elif status == 404:
			print(str(status)+' :: Not found')
		elif status == 406:
			print(str(status)+' :: Not acceptable')
		elif status == 410:
			print(str(status)+' :: Gone')
		elif status == 420:
			print(str(status)+' :: Enhance your Calm - rate limited')
		elif status == 422:
			print(str(status)+' :: Unprocessable entity')
		elif status == 429:
			print(str(status)+' :: Too many requests')
		elif status == 500:
			print(str(status)+' :: Internal server error')
		elif status == 502:
			print(str(status)+' :: Bad gateway')
		elif status == 503:
			print(str(status)+' :: Service unavailable')
		elif status == 504:
			print(str(status)+' :: Gateway timeout')
		else:
			print(str(status)+' :: Unknown')

def signal_handler(signal, frame):
	print('Tweeting [DEACTIVATED] status and terminating program...')
	api.update_status(status=f'{datetime.datetime.now()} :: [DEACTIVATED]')
	sys.exit(0)

# Handle ctl-c and ctrl-z signals
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTSTP, signal_handler)

global api
auth = tweepy.OAuthHandler('', '')
auth.secure = True
auth.set_access_token('', '')
api = tweepy.API(auth)
print(f'Logged in as {api.me().name}\n=========================')
print('Tweeting [ACTIVATED] status...')
api.update_status(status=f'{datetime.datetime.now()} :: [ACTIVATED]')
stream = Stream(auth, StdOutListener())
stream.userstream()
