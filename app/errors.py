from flask import render_template
from flask_login import current_user
from app import app, db
import logging


logger = logging.getLogger(__name__)


@app.errorhandler(404)
def not_found_error(error):
    logger.info('%s - error 404' % current_user.username)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    logger.info('%s - error 500' % current_user.username)
    db.session.rollback()
    return render_template('500.html'), 500

