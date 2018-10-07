from flask_testing import TestCase
from flask import Flask
from app import app, db
from flask_sqlalchemy import SQLAlchemy
import request_history


# create db in memory
# use fixtures


class RequestHistoryTest(TestCase):
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + '?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    
    def create_app(self):
        app = Flask(__name__)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def test_series_name_is_saved(self):
        username = 'nicolas'
        series_name = 'one punch man'
        volume_name = '01 - justice and baldness'
        url = 'hellokitty.com/opm'

        request_history.save_request(username, series_name, volume_name, url)
        actual_info = request_history.load_request(username)

        expected_info = [{'series': series_name, 'volume': volume_name, 'url': url}]

        self.assertEqual(expected_info, actual_info)


