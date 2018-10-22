import os

import redis
from flask import Flask, redirect, url_for
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
socketio = None
rds = None


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:pass@localhost:3306/ebook?charset=utf8',
        SQLALCHEMY_TRACK_MODIFICATIONS=True
    )
    global socketio
    socketio = SocketIO(app)

    global db
    db.init_app(app)

    global rds
    rcp = redis.ConnectionPool(host='localhost', port=6379, db=0)
    rds = redis.StrictRedis(connection_pool=rcp)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def index():
        return redirect(url_for('convert.index'))

    from . import database
    database.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import convert
    app.register_blueprint(convert.bp)
    app.add_url_rule('/', endpoint='index')

    from . import file
    app.register_blueprint(file.bp)

    return app
