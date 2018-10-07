import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.urandom(20)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db' + '?check_same_thread=False') \
                              or os.environ.get('DATABASE_URL') + '?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['en', 'ja']
