# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2019-03-26 23:11:14
'''
BEGIN
function:
    User Register Service
END
'''

import random
from nameko.rpc import rpc
import sys
sys.path.append("..")
from dependence.services import RedisService


class RegisterService(object):
    name = "register"

    def __init__(self):
        self.redis_handle = RedisService()

    @rpc
    def check_registered(self, u_id):
        is_registered, user_data = \
            self.redis_handle.check_registered_and_get_info(u_id)
        if is_registered:
            return user_data
        return None

    @staticmethod
    def generate_u_id():
        """
        Test Function
        """
        return str(random.randint(7000000, 9999999))

    @rpc
    def register(self, email, user_data):
        u_id = self.redis_handle.check_email_is_registered(email)
        if u_id:
            return u_id, "already registered."
        u_id = self.generate_u_id()
        register_result = self.redis_handle.register(u_id, email, user_data)
        if register_result:
            return u_id, ""
        return None, "register failed."
