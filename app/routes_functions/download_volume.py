import io
from scraper import scraper


def format_url(input_url):
    input_url = 'https://ncode.syosetu.com/' + input_url
    if input_url[-1] is not '/':
        input_url += '/'
    return input_url


def download_one_volume(source_info, volume_name):
    memory_file = io.BytesIO()
    memory_file = scraper.generate_single_volume_to_memory(memory_file, source_info, volume_name)
    memory_file.seek(0)
    return memory_file


def download_all_volumes(source_info):
    memory_file = io.BytesIO()
    memory_file = scraper.generate_all_volumes_to_memory(memory_file, source_info)
    memory_file.seek(0)
    return memory_file