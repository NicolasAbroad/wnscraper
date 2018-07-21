# parse_info.py - parses string data


def original_source_info():
    source_info = {'syosetu':{
                        'html':{'series_name': ('p', 'novel_title'),
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


def correct_volume_name(volume_name):
    replace_dict = {'　': ' '}
    for key in replace_dict:
        volume_name = volume_name.replace(key, replace_dict[key])
    return volume_name
