from setuptools import find_packages, setup

setup(
    name='web',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask', 'flask_socketio', 'flask_sqlalchemy', 'werkzeug', 'sqlalchemy', 'pymysql', 'click', 'celery', 'redis',
        'gevent'
    ]
)
