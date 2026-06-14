from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["jerry"]

users_col = db["users"]
memory_col = db["memory"]

