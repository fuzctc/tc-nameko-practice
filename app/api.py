# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2019-03-27 07:58:11
'''
BEGIN
function:
    Comment API
return:
    code:0 success
END
'''

import time
import random
from flask import Flask, request, jsonify
from flasgger import Swagger
from nameko.standalone.rpc import ClusterRpcProxy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="app running port", type=int, default=5000)
parse_args = parser.parse_args()

app = Flask(__name__)
Swagger(app)

CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost"}


@app.route('/api/v1/comment', methods=['POST'])
def comment():
    """
    Comment API

    Parameters Explain:

        timestamp    评论时间
        u_id         用户id
        content      评论内容
        article_id   文章ID
        article_u_id 文章作者用户id
        parent_comment_id 父评论id (optional)
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: comment
          properties:
            timestamp:
              type: integer
            u_id:
              type: string
            content:
              type: string 
            article_id:
              type: integer
            article_u_id:
              type: integer
            parent_comment_id:
              type: integer
    responses:
      code: 
        description: 0 Comment Success! 
      message: 
        description: Error Message! 
      data:
        description: return comment_id
    """
    data = request.json
    article_u_id = data.get("article_u_id")
    u_id = data.get("u_id")
    code, message = 0, ""
    if not article_u_id or not u_id:
        code, message = 10003, "article_u_id or u_id is null."
        response = dict(code=code, message=message, data="")
        return jsonify(response)
    with ClusterRpcProxy(CONFIG) as rpc:
        user_data = rpc.register.check_registered(u_id)
        if not user_data:
            code, message = 10004, "You need to register to comment."
            response = dict(code=code, message=message, data="")
            return jsonify(response)

        # push message
        print("Push Message: article_u_id: {}".format(article_u_id))
        result, message = rpc.push.push(article_u_id, data.get("content"))
        print("push result: {}, message: {}".format(result, message))

    # save comment data
    print("Save Comment Data: article_id: {} content: {}".format(
        data.get("article_id"), data.get("content")))

    data = dict(comment_id=int(time.time()))
    response = dict(code=0, message="", data=data)
    return jsonify(response)


@app.route('/api/v1/register', methods=['POST'])
def register():
    """
    Register API

    Parameters Explain:

        timestamp    注册时间
        email        注册邮箱
        name         名称 
        language     语言
        country      国家
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: data
          properties:
            timestamp:
              type: integer
            email:
              type: string
            name:
              type: string
            language:
              type: string 
            country:
              type: string
    responses:
      code: 
        description: 0 register success. 
      message: 
        description: Error Message! 
      data:
          description: return u_id
    """

    user_data = request.json
    email = user_data.get("email")
    code, message = 0, ""
    if not email:
        code, message = 10000, "email is null."
        response = dict(code=code, message=message, data="")
        return jsonify(response)
    u_id = None
    with ClusterRpcProxy(CONFIG) as rpc:
        u_id, message = rpc.register.register(email, user_data)
    if message:
        code = 10001
    data = dict(u_id=u_id)
    response = dict(code=code, message=message, data=data)
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(parse_args.port), debug=True)
