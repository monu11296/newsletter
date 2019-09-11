import flask
import time
import threading
import math
from flask import jsonify, request, Blueprint, render_template
from sqlalchemy import String
from models import *
from flask_mail import Message
from application import app, mail


api = Blueprint('api', __name__)

def convert_row_to_dict(row):
    row_data = {column.name: str(getattr(row, column.name)) for column in row.__table__.columns}
    return row_data

@api.route('/')
def index():
    return 'I\'m the home page'


@api.route('/subscribers', methods=['GET'])
def get_active_users():

    users = flask.g.session.query(Subscriber).filter(Subscriber.status=='active').all()
    subs_list = [convert_row_to_dict(user) for user in users]

    return jsonify({'subscribers': subs_list}), 200


@api.route('/subscribe', methods=['POST'])
def subscribe_user():

    name = request.form.get('first_name')
    email = request.form.get('email')

    subscriber = Subscriber(first_name=name, email=email)
    flask.g.session.add(subscriber)
    flask.g.session.commit()
    return jsonify({'result': 'success', 'message': f'Subscription added for {subscriber.first_name}.'}), 200
    

@api.route('/unsubscribe', methods=['POST'])
def unsubscribe_user():

    email = request.form.get('email')

    subscriber = flask.g.session.query(Subscriber).filter(Subscriber.email == email).one()
    subscriber.status = 'inactive'
    subscriber.updated_at = datetime.datetime.now()
    flask.g.session.commit()
    return jsonify({'result': 'success', 'message': f'User {subscriber.first_name} has been unsubscribed'}), 200
    

@api.route('/new-article', methods=['POST'])
def publish_new_article():

    subject = request.form.get('subject')
    preview_text = request.form.get('preview_text')
    article_url = request.form.get('article_url')
    
    news_item = NewsItem(subject=subject, preview_text=preview_text, article_url=article_url)
    flask.g.session.add(news_item)
    flask.g.session.commit()
    return jsonify({'result': 'success', 'message': f'Published New Article: {news_item.subject}'}), 200


@api.route('/articles', methods=['GET'])
def get_all_articles():
    
    news_items = flask.g.session.query(NewsItem).all()
    news_items_list = [convert_row_to_dict(item) for item in news_items]

    return jsonify({'articles': news_items_list}), 200


@api.route('/send-mail', methods=['GET'])
def send_mails():
    start_time = datetime.datetime.now()
    data = flask.g.session.query(NewsItem).filter().first()

    # list of active subscribers who have not received an email for a particular item
    try:
        subscribers = flask.g.session.query(Subscriber).filter(
            Subscriber.status=='active',
            ~Subscriber.news_item_received.any(
                NewsItem.id.cast(String).like(str(data.id))
                )
            ).all()
            
    except Exception as e:
        return str(e)

    # return jsonify({'users_not_notified': [convert_row_to_dict(row) for row in subscribers]}), 200
    threads = []
    j=0
    for i in range(1, math.ceil(len(subscribers)/10) + 1):
        # send 10 emails in a thread
        recipients = subscribers[j:(i*10)]
        t = threading.Thread(target=send_mail, args=(recipients, data))
        j = i*10
        threads.append(t)
        t.start()
        
    for index, thread in enumerate(threads):
        thread.join()

    # update database for sent emails
    flask.g.session.commit()
    print((datetime.datetime.now() - start_time).total_seconds())
    return jsonify({'message': 'mails_sent'}), 200


def send_mail(recipients: list, data: dict):
    try:
        with app.app_context():
            with mail.connect() as conn:
                for r in recipients:

                    msg = Message(sender='shaily.sangwan@gmail.com', recipients=[r.email], subject=data.subject)
                    msg.body = f"{data.preview_text}\n To read more, please visit {data.article_url}"
                    msg.html = render_template('article-template.html', username=r.first_name, preview_text=data.preview_text, article_url=data.article_url)
                    conn.send(msg)

                    # save records for sent emails
                    r.news_item_received.append(data)

    except Exception as e:
        return str(e)

    return {'message': f'emails sent to {len(recipients)} users for the article: {data.subject}'}


@api.route('/send-mails-without-threading', methods=['GET'])
def send_mails2():
    start_time = datetime.datetime.now()
    data = flask.g.session.query(NewsItem).first()
    subscribers = flask.g.session.query(Subscriber).filter(Subscriber.status=='active').all()
    resp = send_mail(subscribers, data)
    if resp:
        flask.g.session.commit()
    print((datetime.datetime.now() - start_time).total_seconds())
    return jsonify(resp), 200