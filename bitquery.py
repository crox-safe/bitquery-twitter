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
