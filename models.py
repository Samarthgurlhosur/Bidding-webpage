from __future__ import annotations
import sys

# Python 3.13 compatibility fix for SQLAlchemy
if sys.version_info >= (3, 13):
    import typing
    typing.TypingOnly = object

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    points = db.Column(db.Integer, default=1000)
    items_won = db.relationship('Item', backref='owner', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    item_type = db.Column(db.String(20))  # 'tool' or 'algorithm'
    base_price = db.Column(db.Integer)
    sold_to = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    final_price = db.Column(db.Integer, nullable=True)
    is_auctioned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    bid_amount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    team = db.relationship('Team', backref='bids')
    item = db.relationship('Item', backref='bids')