# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2019-03-26 23:14:11
'''
BEGIN
function:
    Redis Service
return:
    code:0 success
END
'''

import redis
import json
from . import config


class RedisClient(object):
    """
    redis client
    """
    redis_client = {}

    @staticmethod
    def reload_redis(host, port, select_db):
        """
        function: reload redis object
        """
        return redis.StrictRedis(
            host=host,
            port=port,
            db=select_db,
            password="",
            decode_responses=True)

    @classmethod
    def get_redis(cls, redis_name, host, port, select_db):
        """
        function: get redis client
        """
        if redis_name not in cls.redis_client:
            cls.redis_client[redis_name] = cls.reload_redis(
                host, port, select_db)
        return cls.redis_client.get(redis_name)


class RedisService(object):
    def __init__(self):
        self.redis_instance = RedisClient.get_redis(
            config.REDIS_NAME, config.REDIS_HOST, config.REDIS_PORT,
            config.REDIS_DB)
        self.users_key = "users"
        self.users_data_key = "users_data"

    def check_registered_and_get_info(self, u_id):
        """
        Check if the user is registered and return user information \
                if registered.
        """
        user_data = self.redis_instance.hget(self.users_data_key, u_id)
        if not user_data:
            return False, None
        return True, json.loads(user_data)

    def check_email_is_registered(self, email):
        u_id = self.redis_instance.hget(self.users_key, email)
        return u_id

    def register(self, u_id, email, data):
        self.redis_instance.hset(self.users_key, email, u_id)
        result = self.redis_instance.hset(self.users_data_key, u_id,
                                          json.dumps(data))
        return result
