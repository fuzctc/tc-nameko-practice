# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2019-03-26 23:11:14
'''
BEGIN
function:
    Push Service
END
'''

import random
from nameko.rpc import rpc, RpcProxy
import sys
sys.path.append("..")
from dependence.services import RedisService


class PushService(object):
    name = "push"

    register_rpc = RpcProxy("register")

    @rpc
    def push(self, u_id, content):
        user_data = self.register_rpc.check_registered(u_id)
        if not user_data:
        print("User:{} not existed.".format(u_id))
            return False, "not registered."
        language, country = user_data["language"], user_data["country"]

        # get language push content
        print("Push Progress: u_id: {} language: {}, country: {}, content: {}".
              format(u_id, language, country, content))
        
        return True, "push success."
