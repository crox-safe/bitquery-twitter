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
