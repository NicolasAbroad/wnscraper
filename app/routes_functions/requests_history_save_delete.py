from app import db
from app.models import requesthistory
from flask_login import current_user
from scraper.get_info import parse_info


def save_single(source_info, volume_number, volume_name):
    series_name = parse_info.retrieve_series_name_from(source_info)
    input_url = parse_info.retrieve_input_url_from(source_info)

    single = {'series_name': series_name, 'volume_name': volume_name,
              'volume_number': volume_number, 'url': input_url, 'user_id': current_user.id}
    db.session.execute(requesthistory.__table__.insert(), single)
    db.session.commit()


def save_all(source_info):
    series_name = parse_info.retrieve_series_name_from(source_info)
    volume_names = parse_info.retrieve_volume_names_from(source_info)
    input_url = parse_info.retrieve_input_url_from(source_info)

    requests = [{'series_name': series_name, 'volume_name': volume_names[volume_number],
                'volume_number': volume_number, 'url': input_url,
                'user_id': current_user.id} for volume_number in volume_names]
    db.session.execute(requesthistory.__table__.insert(), requests)
    db.session.commit()


def delete_single(request_id):
    requesthistory.query.filter_by(id=request_id).delete()
    db.session.commit()


def delete_all(user_id):
    requesthistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()
