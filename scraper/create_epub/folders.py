# folders.py - Creates series folder for client download requests
import os


def create_series_folder(series_name):
    try:
        os.makedirs('./download')
    except OSError:
        pass
    try:
        os.makedirs('./download/{}'.format(series_name))
    except OSError:
        pass
