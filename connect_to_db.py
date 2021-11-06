import os
import redis
from dotenv import load_dotenv


def connect_to_db(db):
    load_dotenv()

    return redis.Redis(host=os.getenv("REDIS_HOST"),
                       port=os.getenv("REDIS_PORT"),
                       password=os.getenv("REDIS_PASSWORD"),
                       db=db)
