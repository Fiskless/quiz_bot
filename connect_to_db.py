import os
import redis


def connect_to_db():

    return redis.Redis(host=os.getenv("REDIS_HOST"),
                       port=os.getenv("REDIS_PORT"),
                       password=os.getenv("REDIS_PASSWORD"))
