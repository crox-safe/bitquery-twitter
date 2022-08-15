# How to Create a Whale Alert Like Service with Bitquery

# Table of Contents
1. [Introduction](#Introduction)
2. [Creating The Query](#creating-the-query)
3. [Getting the Twitter API and setting up the DB](#getting-the-twitter-api-and-setting-up-the-db)
4. [Developing The Script](#developing-the-script)
5. [Installation and usage](#installation-and-usage)


## Introduction

**If you just want to download the code you can click [here](#installation-and-usage)**

In this article we will see how to make a whale alert as a service that will have the following characteristics:

- Easy to implement
- Easy to modify
- Easy to understand

Before starting to understand the code you have to have some knowledge in the following aspects:
- Python
- Bitquery
- A little bit of MongoDB
- A little bit of the Twitter API

You don't need to be an expert in the above, as the code and the query involved is very simple to understand.

#### How the bot works:
The bot works in a very simple way, it makes a request to bitquery to later process the hash, if the hash of some transaction exists in our database we will not do anything, but if that transaction does not exist, we will add it to our db and then we will make a tweet with the details of our transaction. All this will be repeated every 60 seconds (clearly you can change this).

![bitquery-twitter-diagram](https://user-images.githubusercontent.com/82739614/184578537-4a4fb862-89d0-42e4-a56b-e1a4e1700cb5.jpg)


## Creating The Query
To obtain the data we will use the following [query](https://graphql.bitquery.io/ide/Transactinos-Based-on-Amount-And-Date):

```gql
query  {
  ethereum(network: ethereum) {
    transfers(options: {desc: "block.timestamp.time", limit: 50}, 
      amount: {gt: 500000}, time: {since: "2022-08-13"}, 
      currency: {is: "0xdac17f958d2ee523a2206206994597c13d831ec7"}) {
      block {
        timestamp {
          time(format: "%Y-%m-%d %H:%M:%S")
        }
        height
      }
      sender {
        address
        annotation
      }
      receiver {
        address
        annotation
      }
      transaction {
        hash
      }
      amount
      currency {
        symbol
      }
      external
    }
  }
}
```

In this query what we are telling Bitquery is the following: I want a total of `50 transactions` that have an `amount greater than 500,000` `from the date 2022-08-13`, on the `ethereum blockchain` and for the [USDT token](https://explorer.bitquery.io/ethereum/token/0xdac17f958d2ee523a2206206994597c13d831ec7). At the time of writing this article it is August 13, so I will get the last 50 transactions with the characteristics I put.

## Getting the Twitter API and setting up the DB

#### Twitter Credentials
To get the credentials to use the Twitter API you can visit [here](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api). Remember to enable OAuth 1.0a and then enable read-write (remember to regenerate the credentials).

#### MongoDB Installation
To install the MongoDB database you can go [here](https://www.mongodb.com/try/download/community). To know more about the installation on linux you can visit [here](https://www.mongodb.com/docs/manual/administration/install-on-linux/). Make sure that the installation of MongoDB has been successful.


## Developing the script 
Before developing we will need to install the following modules:

```
pymongo==4.1.1
requests==2.28.1
tweepy==4.10.0
```

> You can install it using `pip install <module>` (or `pip3`, it depends on how you have it installed).



We will create an .env file to save the Twitter and Bitquery credentials.

```
CONSUMER_KEY=
CONSUMER_SECRET=
ACCESS_TOKEN=
ACCESS_TOKEN_SECRET=
DB_URL = "localhost:27017"
DB_NAME = "twitter-bot"
COL_NAME = "transactions"
BITQUERY_API_KEY=
```
> Here you should put the corresponding data, the DB section can be left as it is.


To start developing the project we will create the `bitquery.py` file, practically the same as the tutorial uploaded [here](https://community.bitquery.io/t/how-to-use-bitquery-with-python/1163).

```py
#bitquery.py
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BITQUERY_API_KEY = os.getenv('BITQUERY_API_KEY')


def get_last_transactions(network, token, limit, since, amount):

    query = """
query ($network: EthereumNetwork!, $token: String!, $limit: Int!, 
  $since: ISO8601DateTime, $amount: Float!) {
  ethereum(network: $network) {
    transfers(options: {desc: "block.timestamp.time", limit: $limit}, 
      amount: {gt: $amount}, time: {since: $since}, 
      currency: {is: $token}) {
      block {
        timestamp {
          time(format: "%Y-%m-%d %H:%M:%S")
        }
        height
      }
      sender {
        address
        annotation
      }
      receiver {
        address
        annotation
      }
      transaction {
        hash
      }
      amount
      currency {
        symbol
      }
      external
    }
  }
}
"""


    params = {"network": network, "token": token, "limit": limit, "since": since, "amount": amount} # Here we put the variables
    json     = {"query"     : query, "variables": params}
    headers  = {"X-API-KEY" : BITQUERY_API_KEY}

    request = requests.post("https://graphql.bitquery.io/", json=json, headers=headers)

    if request.status_code == 200:
        data = request.json()
        return data
    else: 
        print("Something unexpected happened.")
```

#### Explanation of the modules:
- `requests` - It will allow us to send the request to the bitquery servers.
- `json` - With this we will be able to manipulate the results that bitquery gives us in a more pythonic way.
- `datetime` - We will use it to obtain the current day in UTC
- `os` - Will allow us to use the .env file (to get Bitquery API Key).
- `dotenv` - This is for using our environment variables in Python.

#### Explanation of the script: 
This script contains the function `get_last_transactions` which receives 5 arguments, which are: `network`, `token`, `limit`, `since`, `amount`.

- `network` - To define a network (`ethereum`, `bsc`, `matic`, etc)
- `token` - A contract token (e.g. `0xdac17f958d2ee523a2206206994597c13d831ec7 USDT`)
- `limit` - limit for the output of our query
- `since` - Date from when we want to get the data
- `amount` - Filter to get transactions greater than this amount

Now we will create the `twitter.py` file that will allow us to manage our Twitter credentials as well as post a tweet every time we see a transaction.

```py
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
```

#### Explanation of the modules:

- `tweepy` - Allows us to connect to the Twitter API in order to make our tweet.


Now we will create the file for the connection with MongoDB `database.py`. It will allow us to create two main functions, one to query the database if a transaction (by the hash) exists in the database, the other one to add our transaction to the database.

```py
import datetime
from pymongo import MongoClient


class Database:
    def __init__(self, uri, database_name, collection):
        self._client = MongoClient(uri)
        self.db = self._client[database_name]
        self.col = self.db[collection]

    def new_tx(self, hash, time, sender, receiver, amount, symbol, external):
        return dict(
            hash=hash,
            time=time,
            sender=sender,
            receiver=receiver,
            amount=amount,
            symbol=symbol,
            external=external,
        )

    def add_tx(self, hash, time, sender, receiver, amount, symbol, external):
        tx = self.new_tx(hash, time, sender, receiver, amount, symbol, external)
        self.col.insert_one(tx)

    def tx_exist(self, hash):
        tx = self.col.find_one({"hash": hash})
        return True if tx else False
```

We will also create the `main.py` file, which will be the file we will execute. This file has two main functions, one of them is `check_transactions`, which we will call every 60 seconds to verify the new transactions, this function will evaluate the transactions that bitquery gives us to see if there is a transaction that is not in the DB to see if it tweets it. The other function is `main`, which will create an infinite loop that will call the function `check_transactions` as well as `time.sleep` every 60 seconds.

```py
from database import Database
from bitquery import get_last_transactions
import time
import os
from datetime import datetime
from twitter import update_status
from dotenv import load_dotenv

load_dotenv()

# Config for MongoDB
DB_URL = os.getenv('DB_URL')
DB_NAME = os.getenv('DB_NAME')
COL_NAME = os.getenv('COL_NAME')

db = Database(DB_URL, DB_NAME, COL_NAME)


def check_transactions():

    print("Checking transactions")

    since = datetime.utcnow().strftime('%Y-%m-%d') 
    
    txs = get_last_transactions("ethereum", "0xdac17f958d2ee523a2206206994597c13d831ec7", 50, since, 500000)

    for transaction in txs['data']['ethereum']['transfers']:

        tx_hash = transaction['transaction']['hash']
        tx_time = transaction['block']['timestamp']['time']
        tx_sender = transaction['sender']['address']
        tx_receiver = transaction['receiver']['address']
        tx_amount = transaction['amount']
        tx_symbol = transaction['currency']['symbol']
        tx_external = transaction['external']


        if (db.tx_exist(tx_hash)):
            pass
        else:
            db.add_tx(tx_hash, tx_time, tx_sender, tx_receiver, tx_amount, tx_symbol, tx_external)

            time.sleep(1)
            msg = f"{tx_amount} #{tx_symbol} transferred from {tx_sender[0:4] + '...' + tx_sender[38:42]} to {tx_receiver[0:4] + '...' + tx_receiver[38:42]} \n\nhttps://explorer.bitquery.io/ethereum/tx/{tx_hash}/" 
            tweet = update_status(msg)

def main():
    
    try:
        while True:
            check_transactions()
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
            pass

if __name__ == '__main__':
    main()
```

#### Explanation of the modules:

- `time` - It will serve as a "timer" which we will use every 60 seconds.
- `database`, `bitquery`, `twitter` - These are modules that we will import from the functions we created earlier.



## Installation and usage

To clone the repository we will do the following:

`git clone https://github.com/crox-safe/bitquery-twitter/`

If you don't have git you can download the code in Code --> Download ZIP and then extract the ZIP

Once you have everything downloaded we will enter the file

`cd bitquery-twitter`

Now we will install the modules:

`pip install -r requirements.txt`

> Remember that it can be `pip`, `pip3`, etc.

We will rename the `.env_sample` file to `.env`. After that we will fill in with our credentials

And finally we can run the code with:

`python main.py`

> Remember that it can be `python`, `python3`, etc.


