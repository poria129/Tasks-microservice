from pymongo import MongoClient


class MongoDBManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance.client = None
        return cls._instance

    def __enter__(self):
        if self.client is None:
            self.client = MongoClient("localhost", 27017)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.client is not None:
            self.client.close()
            self.client = None

    def get_database(self, database_name):
        if self.client is not None:
            return self.client[database_name]
        return None

    @property
    def auth_db(self):
        return self.get_database("auth_db")

    @property
    def auth(self):
        return self.auth_db["auth"]
