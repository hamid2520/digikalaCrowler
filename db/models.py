from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from db.connection import Base
import datetime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True)
    password = Column(String(64))
    email = Column(String(128), nullable=True)
    phone = Column(String(10), nullable=True)
    first_name = Column(String(128))
    last_name = Column(String(128))

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'first_name': self.first_name,
            'last_name': self.last_name
        }


class Token(Base):
    __tablename__ = 'tokens'
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User', foreign_keys=[user_id])
    key = Column(String(64), primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)

    def serialize(self):
        return {
            'key': self.key,
        }


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User', foreign_keys=[user_id])
    product_id = Column(Integer)
    text = Column(String(256))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    score = Column(Integer, default=0)
    deleted = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.serialize(),
            'text': self.text,
            'product_id': self.product_id,
            'score': self.score,
            'date_created': self.date_created
        }


class Rate(Base):
    __tablename__ = 'rates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User', foreign_keys=[user_id])
    comment_id = Column(Integer, ForeignKey(Comment.id))
    comment = relationship('Comment', foreign_keys=[comment_id])
    polarity = Column(Integer, default=0)

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.serialize(),
            'polarity': self.polarity,
            'comment': self.comment.serialize(),
        }
