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

    