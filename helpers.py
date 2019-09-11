import flask
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

DBSESSIONFACTORY = None

def set_request():

    if not hasattr(flask.g, "session"):
        flask.g.session = create_session(flask.current_app.config["SQLALCHEMY_DATABASE_URI"])

def end_request(exception=None):

    flask.g.session.remove()

def create_session(db_url=None):

    global DBSESSIONFACTORY

    if DBSESSIONFACTORY is None or db_url != f'{DBSESSIONFACTORY.kw["bind"].engine.url}':

        engine = create_engine(db_url, echo=False, pool_recycle=3600)
        DBSESSIONFACTORY = sessionmaker(bind=engine)

    scopedsession = scoped_session(DBSESSIONFACTORY)
    return scopedsession

