# query_info.py - queries data from website


import requests
import bs4

from . import parse_info


def get_page_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.content, "html.parser")
    return soup


# Use to get serie's name and author
def get_string(soup, html_id):
    for name in soup.find_all(html_id[0], class_=html_id[1]):
        return name.text


def get_index(soup, html_index):
    index = soup.find(html_index[0], class_=html_index[1])
    return index


def get_index_children(index):
    index_children = index.children
    return index_children


def volumes_exist(index_children, vol_and_chap):
    for index_child in index_children:
        child = str(index_child)
        if vol_and_chap[0] in child:
            return True
    return False


# Use if volumes exist

def scrape_chapter_info_by_volume(index_children, name_id, target_info_id):
    chapter_info_dict = {}
    volume = ''
    volume_id = name_id[0]
    chap_id = name_id[1]
    for index_child in index_children:
        index_child_str = str(index_child)
        if volume_id in index_child_str:
            volume = index_child.string
            volume = parse_info.format_volume_name_to_html(volume)
            chapter_info_dict.setdefault(volume, [])         # index_child_str = volume name
        elif chap_id in index_child_str:
            ch_name = index_child.find(target_info_id[0])
            chapter_info_dict[volume] += [(ch_name.text, ch_name.attrs[target_info_id[1]])]
    return chapter_info_dict
"""

def scrape_chapter_info_by_volume(index_children, name_id, target_info_id):
    combined_dict = {}
    chapter_info_dict = {}
    volume_names = {}

    volume = ''
    volume_nb = 1
    volume_id = name_id[0]
    chap_id = name_id[1]
    for index_child in index_children:
        index_child_str = str(index_child)
        if volume_id in index_child_str:
            # Add volume name as key to chapter info dict
            volume_name = index_child.string
            volume_name = parse_info.format_volume_name_to_html(volume_name)
            chapter_info_dict.setdefault(volume_name, [])         # index_child_str = volume name

            # Add volume number as key to volume names // Assign volume name to key
            volume_nb_formatted = '{0:02d}'.format(volume_nb)
            volume_names[volume_nb_formatted] = volume_name
        elif chap_id in index_child_str:
            ch_name = index_child.find(target_info_id[0])
            chapter_info_dict[volume] += [(ch_name.text, ch_name.attrs[target_info_id[1]])]
    combined_dict['info'] = chapter_info_dict
    combined_dict['names'] = volume_names
    return combined_dict
"""

# Use if volumes don't exist
def get_dict_key(series_name):
    chapter_info_dict = {}
    chapter_info_dict.setdefault(series_name, [])
    return chapter_info_dict


# Use if volumes don't exist
def scrape_all_chapter_info(chapter_info_dict, index_children, name_id, series_name, target_info_id):
    def inner(chapter_info_dict, index_children, name_id, series_name, target_info_id):
        local_chapter_info_dict = chapter_info_dict
        volume = series_name
        for index_child in index_children:
            index_child_str = str(index_child)
            if name_id[1] in index_child_str:
                ch_name = index_child.find(target_info_id[0])
                local_chapter_info_dict[volume] += [(ch_name.text, ch_name.attrs[target_info_id[1]])]
        return local_chapter_info_dict
    return inner(chapter_info_dict, index_children, name_id, series_name, target_info_id)


def volume_info(source, source_info, toc_html):
    index = get_index(toc_html, source_info['html_index'])
    index_children = get_index_children(index)
    if volumes_exist(index_children, source_info['vol_and_chap']):
        volume_info = scrape_chapter_info_by_volume(index_children, source_info)
    else:
        volume_info = get_dict_key(series_name)
        volume_info = scrape_all_chapter_info(volume_info, index_children, source_info['vol_and_chap'], series_name, source_info['chap_name_url'])
    return volume_info

