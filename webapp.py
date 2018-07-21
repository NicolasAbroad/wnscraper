#! python3

from flask import Flask, flash, redirect, render_template, request, session, send_file
import os
import sys

import zipfile
import io

sys.path.append('./scraper')
import main

app = Flask(__name__)


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/')
def redir_home():
    return redirect('index')


@app.route('/index', methods=['GET', 'POST'])
def home():
#    if not session.get('logged_in'):
#        return render_template('login.html')
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == '' and request.form['password'] == '':
        session['logged_in'] = True
    else:
        flash('wrong password')
    return redirect('index')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect('index')


@app.route('/process', methods=['POST'])
def process():
    if request.method == 'POST':
#        if session:
#            session.clear()
        input_url = request.form['input_content']
        source = main.get_source(input_url)
        source_info = main.get_info(input_url, source)

        session['info'] = source_info
        session['url'] = input_url

        series_name = source_info[source]['info']['series_name']
        series_name_formatted = (series_name, series_name.replace(' ', '%20'))

        volume_names = source_info[source]['info']['volume_names']
        volume_names_formatted = []
        for index, volume in enumerate(volume_names.keys()):
            volume_names_formatted += [('{0:02d}'.format(index+1) + ' - ' + volume, '{0:02d}'.format(index+1) + '%20-%20' + volume.replace(' ', '%20'), volume)]

        return render_template('process.html', series_name=series_name_formatted, volume_names=volume_names_formatted)


""" WORKING!
@app.route('/download/<series_name>/<volume_name_formatted>/<volume_name>', methods=['POST'])
def download(series_name, volume_name_formatted, volume_name):
    if request.method == 'POST':
        source_info = session.get('info')
        input_url = session.get('url')
        source = main.get_source(input_url)
        source_info = main.get_info(input_url, source)
        main.generate_single_volume(source_info, volume_name)
        return send_file('download/{}/{}.epub'.format(series_name, volume_name_formatted), as_attachment=True)
WORKING! """


@app.route('/download/<series_name>/<volume_name_formatted>/<volume_name>', methods=['POST'])
def download(series_name, volume_name_formatted, volume_name):
    if request.method == 'POST':
        input_url = session.get('url')
        source = main.get_source(input_url)
        source_info = main.get_info(input_url, source)
        memory_file = io.BytesIO()
        memory_file = main.generate_single_volume_memory(memory_file, source_info, volume_name)
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='{}.epub'.format(volume_name_formatted), as_attachment=True)


@app.route('/download_all/<series_name>', methods=['POST'])
def download_all(series_name):
    if request.method == 'POST':
        return send_file('download_all/{}.epub'.format(series_name), as_attachment=True)


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=5000)