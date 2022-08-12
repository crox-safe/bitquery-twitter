import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

# Config for twitter API
CONSUMER_KEY=os.getenv('CONSUMER_KEY')
CONSUMER_SECRET=os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN=os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET=os.getenv('ACCESS_TOKEN_SECRET')


def update_status(msg):
    twitter_auth_keys = {
        "consumer_key"        : CONSUMER_KEY,
        "consumer_secret"     : CONSUMER_SECRET,
        "access_token"        : ACCESS_TOKEN,
        "access_token_secret" : ACCESS_TOKEN_SECRET,
    }

    try:

        auth = tweepy.OAuthHandler(
                twitter_auth_keys['consumer_key'],
                twitter_auth_keys['consumer_secret']
                )
        auth.set_access_token(
                twitter_auth_keys['access_token'],
                twitter_auth_keys['access_token_secret']
                )
        api = tweepy.API(auth)

        tweet = msg
        post_result = api.update_status(status=tweet, card_uri='tombstone://card')

        return True

    except:
        
        return False
