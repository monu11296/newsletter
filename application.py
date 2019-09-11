import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from helpers import set_request, end_request
from flask_mail import Mail

app = Flask(__name__)

db = SQLAlchemy()
mail = Mail()

def create_app():

    from views import api
    app.register_blueprint(api)

    app.config.update(
        SECRET_KEY= os.environ['SECRET_KEY'],
        SQLALCHEMY_DATABASE_URI=os.environ['DATABASE_URL'],
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        MAIL_SERVER='smtp.sendgrid.net',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME='apikey',
        # MAIL_PASSWORD='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'
        MAIL_PASSWORD=os.environ['MAIL_SERVER_API_KEY']
        )

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        db.create_all()

    app.before_request(set_request)
    app.teardown_request(end_request)

    return app
