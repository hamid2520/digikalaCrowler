from flask import request

from db.models import Comment, Rate
from db.connection import db_session
import datetime
import json


def send_comment(user_id):
    if 'text' in request.form and 'product_id' in request.form:
        comment = Comment()
        comment.user_id = user_id
        comment.product_id = request.form['product_id']
        comment.text = request.form['text']
        db_session.add(comment)
        db_session.commit()
        return json.dumps({
            'success': True,
            'comment': comment.serialize()
        })

    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })


def get_comments():
    if 'product_id' in request.args:
        comments = [comment.serialize() for comment in Comment.query.filter(
                Comment.product_id == request.args['product_id'], Comment.verified == True, Comment.deleted == False)]
        return json.dumps({
            'success': True,
            'comments': sorted(comments, key=lambda c: c['date_created'], reverse=True)
        })
    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })


def get_all_comments():
    comments = [comment.serialize() for comment in Comment.query.filter(
        Comment.verified == True, Comment.deleted == False)]
    return json.dumps({
        'success': True,
        'comments': sorted(comments, key=lambda c: c['date_created'], reverse=True)
    })


def set_rate(user_id):
    if 'comment_id' in request.form and 'polarity' in request.form:
        comment = Comment.query.filter(Comment.id == request.form['comment_id']).first()
        if comment is not None:
            rate = Rate.query.filter(Rate.user_id == user_id, Rate.comment_id == comment.id).first()
            if rate is None:
                rate = Rate()
                rate.user_id = user_id
                rate.comment_id = comment.id
            comment.score += request.form['polarity'] - rate.polarity
            rate.polarity = request.form['polarity']
        return json.dumps({
            'success': False,
            'error': 'comment not found'
        })
    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })
