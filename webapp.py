from app import app, db, cli
from app.models import users, requesthistory


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'users': users, 'requesthistory': requesthistory}
