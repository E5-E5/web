import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Player(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'players'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    win = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    lose = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    pat = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    pr = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0.0%')