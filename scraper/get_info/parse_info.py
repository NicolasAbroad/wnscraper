# parse_info.py - parses string data


def original_source_info():
    source_info = {'syosetu':{
                        'html': {'series_name': ('p', 'novel_title'),
                                 'author_name': ('div', 'novel_writername'),
                                 'html_index': ('div', 'index_box'),
                                 'volume': ('div', 'class', 'chapter_title'),
                                 'vol_and_chap': ('chapter_title', 'subtitle'),
                                 'chap_name_url': ('a', 'href'),
                                 'chapter_number': ('div', 'id', 'novel_no'),
                                 'chapter_text': ('div', 'id', 'novel_honbun'),
                                 'url_regex': r'\d+/$'}}}
    return source_info


def format_author(source, author_name):
    if source == 'syosetu':
        author_name = author_name[4:-1]
    return author_name

"""
def extract_volume_names(volume_info):
    volume_names = {}
    for index, volume in enumerate(list(volume_info.keys())):
        volume_name_formatted = '{0:02d}'.format(index+1) + ' - ' + volume
        volume_name_formatted_html = '{0:02d}'.format(index+1) + '%20-%20' + volume.replace(' ', '%20')
        volume_names[volume] = (volume_name_formatted, volume_name_formatted_html)
    return volume_names
"""

def extract_volume_names(index_children, name_id):
    volume_names = {}
    volume_name = ''
    volume_id = name_id[0]
    nb = 1
    for index_child in index_children:
        index_child_str = str(index_child)
        if volume_id in index_child_str:
            volume_name = index_child.string
            volume_name = format_volume_name_to_html(volume_name)

            nb_formatted = '{0:02d}'.format(nb)
            volume_names[nb_formatted] = volume_name
            nb += 1
    return volume_names


def extract_volume_names_and_numbers(volume_info, length=2):
    volume_names = {}
    for index, volume in enumerate(list(volume_info.keys())):
        volume_name = volume
        if length == 2:
            volume_number = '{0:02d}'.format(index+1)
        else:
            volume_number = '{0:03d}'.format(index + 1)
        volume_names[volume_number] = volume_name
    return volume_names


def format_volume_name(volume_number, volume_name):
    volume_name_formatted = '{} - {}'.format(volume_number, volume_name)
    return volume_name_formatted


def format_volume_name_to_html(volume_name):
    replace_dict = {'　': ' '}
    for key in replace_dict:
        volume_name = volume_name.replace(key, replace_dict[key])
    return volume_name


def retrieve_input_url_from(source_info):
    input_url = source_info['input_url']
    return input_url


def retrieve_source_from(source_info):
    source = source_info['source']
    return source


def retrieve_series_name_from(source_info):
    source = retrieve_source_from(source_info)
    series_name = source_info[source]['info']['series_name']
    return series_name


def retrieve_author_name_from(source_info):
    source = retrieve_source_from(source_info)
    author_name = source_info[source]['info']['author_name']
    return author_name


def retrieve_volume_names_from(source_info):
    source = retrieve_source_from(source_info)
    volume_names = source_info[source]['info']['volume_names']
    return volume_names


def retrieve_volume_info_from(source_info):
    source = retrieve_source_from(source_info)
    volume_info = source_info[source]['info']['volume_info']
    return volume_info


def retrieve_uid_from(source_info):
    source = retrieve_source_from(source_info)
    uid = source_info[source]['info']['uid']
    return uid


