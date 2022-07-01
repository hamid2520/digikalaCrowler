from __future__ import absolute_import, division, print_function, unicode_literals
from flask import Flask, request, render_template, Response, jsonify

from crawlers import dg_crawler
from embeding import tf_idf
from db.models import Token, User, Comment
from core import user, comment, product
import json

app = Flask(__name__)


def check_token():
    if 'token' not in request.headers:
        return {
            'success': False,
            'error': 'parameter missing'
        }
    token = Token.query.filter(Token.key == request.headers['token']).first()
    if token is None:
        return {
            'success': False,
            'error': 'invalid token'
        }
    return {
        'success': True,
        'user': token.user
    }


@app.route('/api/v1/register', methods=['POST'])
def register():
    return Response(user.register())


@app.route('/api/v1/login', methods=['POST'])
def login():
    return Response(user.login())


@app.route('/api/v1/check', methods=['POST'])
def check():
    return Response(user.check())


@app.route('/api/v1/product', methods=['GET'])
def get_product():
    return Response(product.get_product())


@app.route('/api/v1/comment', methods=['GET'])
def get_comments():
    return Response(comment.get_comments())


@app.route('/api/v1/comment', methods=['POST'])
def send_comment():
    check = check_token()
    if not check['success']:
        return Response(json.dumps(check))
    return Response(comment.send_comment(check['user']))


@app.route('/api/v1/comment/all', methods=['GET'])
def get_all_comments():
    return Response(comment.get_all_comments())


@app.route('/api/v1/search')
def search():
    return Response(tf_idf.search())


@app.route('/api/v1/product/suggestion', methods=['GET'])
def get_suggestions():
    pass


@app.route('/api/v1/comment/dg', methods=['GET'])
def get_dg_comments():
    return Response(dg_crawler.get_comments())


if __name__ == '__main__':
    app.run()
