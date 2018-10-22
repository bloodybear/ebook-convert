import importlib

if importlib.util.find_spec("web"):
    print("import flask_sqlalchemy for models")
    from web import db

    Base = db.Model
    orm = db
else:
    print("import sqlalchemy for models")
    import sqlalchemy as db
    import sqlalchemy.orm as orm
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()
from datetime import datetime


class User(Base):
    # __tablename__ = 'user'
    # __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r:%r>' % (self.id, self.username)


class Post(Base):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = orm.relationship('User', backref=orm.backref('posts', lazy=True))
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r:%r>' % (self.id, self.title)


class Task(Base):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = orm.relationship('User', backref=orm.backref('tasks', lazy=True))
    src_file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    dst_ext = db.Column(db.String(16), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started = db.Column(db.DateTime, nullable=True)
    elapsed_time = db.Column(db.Integer, nullable=True)
    dst_file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)
    ended = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Task %r:%r>' % (self.id, self.status)


class File(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024), nullable=False)
    ext = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=True)
    path = db.Column(db.String(2048), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<File %r:%r>' % (self.id, self.name)
