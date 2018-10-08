import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.urandom(20)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') + '?check_same_thread=False' \
                              or 'sqlite:///' + os.path.join(basedir, 'app.db' + '?check_same_thread=False')
#    DATABASE_URL=mysql+pymysql://wnscraper:<db-password>@localhost:3306/wnscraper
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['en', 'ja']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
