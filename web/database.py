import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from common.database.models import *


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.drop_all()
    db.create_all()
    db.session.add(User(username='u', password=generate_password_hash('p')))
    db.session.add(User(username='user', password=generate_password_hash('pass')))
    db.session.commit()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)
