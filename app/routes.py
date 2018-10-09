from flask import flash, redirect, render_template, request, session, send_file, url_for
from flask import g
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from werkzeug.urls import url_parse
from app.models import users, requesthistory
from app.forms import LoginForm, RegistrationForm
from scraper import scraper
from scraper.get_info import parse_info
from app.routes_functions import download_volume, requests_history_save_delete
from datetime import datetime
import logging
import requests         # Used for connection error exception


logger = logging.getLogger(__name__)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.locale = str(get_locale())


@app.context_processor
def inject_config_var():
    return dict(CURRENT_LANGUAGE=session.get('language'))


@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html', title=_('Homepage'))


@app.route('/language/<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html', title=_('About'))


@app.route('/scrape', methods=['GET', 'POST'])
@login_required
def scrape():
    return render_template('scrape.html', title=_('Scrape'))


@app.route('/process', methods=['POST'])
@login_required
def process():      #TODO rename
    if request.method == 'POST':
        input_url = request.form['input_url']
        source = scraper.check_source(input_url)
        if source:
            try:
                source_info = scraper.get_info(input_url, source)
            except requests.ConnectionError:
                flash(_("Unable to connect to the webnovel's host website"))
                return redirect(url_for('scrape'))
            session['url'] = input_url
            series_name = parse_info.retrieve_series_name_from(source_info)
            series_name_formatted = (series_name, series_name.replace(' ', '%20'))
            volume_names = parse_info.retrieve_volume_names_from(source_info)
        else:
            flash(_('Please enter a valid url. For example: https://ncode.syosetu.com/n7103ev/'))
            return redirect(url_for('scrape'))
        return render_template('process.html', title=_('Processing...'),
                               series_name=series_name_formatted, volume_names=volume_names)


@app.route('/download/<volume_number>', defaults={'input_url': None}, methods=['POST'])
@app.route('/download/<volume_number>/<input_url>', methods=['POST'])
@login_required
def download(volume_number, input_url=None):            #TODO rename
    if request.method == 'POST':
        if input_url is None:
            input_url = session.get('url')
        else:
            input_url = download_volume.format_url(input_url)
        try:
            source_info = scraper.create_source_info(input_url)
        except requests.ConnectionError:
            flash(_("Unable to connect to the webnovel's host website"))
            return redirect(url_for('scrape'))
        memory_file = download_volume.download_one_volume(source_info, volume_number)
        volume_names = parse_info.retrieve_volume_names_from(source_info)
        volume_name = volume_names[volume_number]
        requests_history_save_delete.save_single(source_info,volume_number, volume_name)
        series_name = parse_info.retrieve_series_name_from(source_info)
        logger.info('%s downloaded one volume - Series: %s - Volume: %s' % (current_user.username, series_name, volume_name))
        volume_name_formatted = parse_info.format_volume_name(volume_number, volume_name)
        return send_file(memory_file, attachment_filename='{}.epub'.format(volume_name_formatted), as_attachment=True)


@app.route('/download_all/<series_name>', methods=['POST'])
@login_required
def download_all(series_name):
    if request.method == 'POST':
        input_url = session.get('url')
        source_info = scraper.create_source_info(input_url)
        memory_file = download_volume.download_all_volumes(source_info)
        requests_history_save_delete.save_all(source_info)
        logger.info('%s downloaded all volumes - Series: %s' % (current_user.username, series_name))
        return send_file(memory_file, attachment_filename='{}.zip'.format(series_name), as_attachment=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        logger.info('New user registered: %s' % user.username)
        flash(_('You have successfully been registered.'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        logger.info('Logged in')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash(_('Logged in as %(username)s', username=user.username))
        return redirect(next_page)
    return render_template('login.html', title=_('Sign in'), form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    logger.info('Logged out')
    flash(_('You have successfully logged out.'))
    return redirect(url_for('index'))


@app.route('/<username>/history')
@login_required
def requests_history(username):
    if username == current_user.username:
        user = users.query.filter_by(username=username).one()
        id = user.id
        requests = requesthistory.query.filter_by(user_id=id).all()
        return render_template('requests_history.html', title=_('Requests history'), user=user, requests=requests)


@app.route('/<username>/history/delete/<request_id>')
@login_required
def delete_single_request(username, request_id):
    if username == current_user.username:
        requests_history_save_delete.delete_single(request_id)
        logger.info('%s deleted one request from history' % current_user.username)
        return redirect(url_for('requests_history', username=current_user.username))
    else:
        logger.warn('Illegal deletion request from %s' % current_user.username)


@app.route('/<username>/history/delete_all')
@login_required
def delete_all_requests(username):
    if username == current_user.username:
        user = users.query.filter_by(username=username).first_or_404()
        user_id = user.id
        requests_history_save_delete.delete_all(user_id)
        logger.info('%s deleted all requests from history' % current_user.username)
        return redirect(url_for('requests_history', username=current_user.username))
    else:
        logger.warn('Illegal deletion request from %s' % current_user.username)


@app.route('/invalid')
def invalid():
    return render_template('invalid.html', title='Invalid url')


@app.route('/github-repository')
def github_repository():
    if current_user.is_authenticated:
        logger.info('%s redirected to github repository' % current_user.username)
    else:
        logger.info('Anonymous user redirected to github repository')
    return redirect('https://github.com/NicolasAbroad/epub_scraper')

"""
@app.route('/debug')
def debug():
    return render_template('debug.html', title='Debug')


@app.route('/debug/users')
def debug_users():
    usernames = users.query.order_by(users.id).all()
    return render_template('debug_users.html', usernames=usernames)


@app.route('/debug/requests')
def debug_requests():
    all_requests = requesthistory.query.order_by(requesthistory.user_id).all()
    return render_template('debug_requests.html', requests=all_requests)


@app.route('/debug/add_requests')
def debug_add_requests():
    n1 = requesthistory(series_name='One Punch Man', volume_number='01', volume_name='Baldness', url='https://ncode.syosetu.com/n7103ev/', user_id=1)
    n2 = requesthistory(series_name='One Punch Man', volume_number='02', volume_name='Justice', url='https://www.google.com/one-punch-man/volume2', user_id=1)
    n3 = requesthistory(series_name='One Punch Man', volume_number='03', volume_name='Caped baldy', url='https://www.google.com/one-punch-man/volume3', user_id=1)
    m1 = requesthistory(series_name='One Piece', volume_number='01', volume_name='Straw Hat', url='https://www.google.com/one-piece/volume1', user_id=2)
    m2 = requesthistory(series_name='One Piece', volume_number='02', volume_name='Rubbery', url='https://www.google.com/one-piece/volume2', user_id=2)
    m3 = requesthistory(series_name='One Piece', volume_number='03', volume_name='Meat', url='https://www.google.com/one-piece/volume3', user_id=2)
    db.session.add(n1)
    db.session.add(n2)
    db.session.add(n3)
    db.session.add(m1)
    db.session.add(m2)
    db.session.add(m3)
    db.session.commit()
    flash('Requests added to db.')
    return redirect(url_for('debug'))


@app.route('/debug/clear_requests')
def debug_clear_requests():
    all_requests = requesthistory.query.all()
    for request in all_requests:
        db.session.delete(request)
    db.session.commit()
    flash(_('Requests erased from db.'))
    return redirect(url_for('debug'))


@app.route('/debug/requests/<username>')
def debug_filter_requests(username):
    user = users.query.filter_by(username=username).one()
    id = user.id
    requests = requesthistory.query.filter_by(user_id=id).all()
    return render_template('debug_requests_filter.html', user=user, requests=requests)


@app.route('/debug/source_info')
def debug_source_info():
    url = "https://ncode.syosetu.com/n7103ev/"
    source_info = scraper.create_source_info(url)
    volume_names = parse_info.retrieve_volume_names_from(source_info)
    volume_keys = volume_names.keys()
    return "%s" % (volume_keys)
"""
