import uuid
import datetime
import flask
from sqlalchemy.dialects.postgresql import UUID
from application import db


class Subscriber(db.Model):

    __tablename__ = 'subscriber'

    Status = ['active', 'inactive']

    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    status = db.Column(db.Enum(*Status, name='user_status'), default='active')
    email = db.Column(db.String(), nullable=False, unique=True)
    registered_at = db.Column(db.TIMESTAMP, default=datetime.datetime.now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP)

    def __repr__(self):
        return f'<id {self.id}>'


SubNewsData = db.Table(
    'subscriber_news_data',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('subscriber.id'), primary_key=True),
    db.Column('news_id', UUID(as_uuid=True), db.ForeignKey('news_item.id'), primary_key=True),
    db.Column('sent_at', db.TIMESTAMP, default=datetime.datetime.now, nullable=False)
    )


class NewsItem(db.Model):

    __tablename__ = 'news_item'

    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, primary_key=True)
    subject = db.Column(db.String(), nullable=False)
    preview_text = db.Column(db.String(), nullable=False)
    article_url = db.Column(db.String(), nullable=False, unique=True)
    sent_to = db.relationship('Subscriber', secondary=SubNewsData, lazy=True, backref=db.backref('news_item_received', lazy=True))
    published_at = db.Column(db.TIMESTAMP, default=datetime.datetime.now, nullable=False)

    def __repr__(self):
        return f'<id {self.id}>'
