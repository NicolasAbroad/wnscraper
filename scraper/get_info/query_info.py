# query_info.py - queries data from website


import requests
import bs4

from . import parse_info


def get_page_html(url):
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.content, "html.parser")
    return soup


# Use to get serie's name and author
def get_string(soup, html_element):
    for name in soup.find_all(html_element[0], class_=html_element[1]):
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
def scrape_chapter_info_by_volume(index_children, name_element, target_info_element):
    def inner(index_children, name_element, target_info_element):
        chapter_info_dict = {}
        volume = ''
        for index_child in index_children:
            index_child_str = str(index_child)
            if name_element[0] in index_child_str:
                volume = index_child.string
                volume = parse_info.correct_volume_name(volume)
                chapter_info_dict.setdefault(volume, [])         # index_child_str = volume name
            elif name_element[1] in index_child_str:
                ch_name = index_child.find(target_info_element[0])
                chapter_info_dict[volume] += [(ch_name.text, ch_name.attrs[target_info_element[1]])]
        return chapter_info_dict
    return inner(index_children, name_element, target_info_element)


# Use if volumes don't exist
def get_dict_key(series_name):
    chapter_info_dict = {}
    chapter_info_dict.setdefault(series_name, [])
    return chapter_info_dict


# Use if volumes don't exist
def scrape_all_chapter_info(chapter_info_dict, index_children, name_element, series_name, target_info_element):
    def inner(chapter_info_dict, index_children, name_element, series_name, target_info_element):
        local_chapter_info_dict = chapter_info_dict
        volume = series_name
        for index_child in index_children:
            index_child_str = str(index_child)
            if name_element[1] in index_child_str:
                ch_name = index_child.find(target_info_element[0])
                local_chapter_info_dict[volume] += [(ch_name.text, ch_name.attrs[target_info_element[1]])]
        return local_chapter_info_dict
    return inner(chapter_info_dict, index_children, name_element, series_name, target_info_element)


def volume_info(source, source_info, toc_html):
    index = get_index(toc_html, source_info['html_index'])
    index_children = get_index_children(index)
    if volumes_exist(index_children, source_info['vol_and_chap']):
        volume_info = scrape_chapter_info_by_volume(index_children, source_info)
    else:
        volume_info = get_dict_key(series_name)
        volume_info = scrape_all_chapter_info(volume_info, index_children, source_info['vol_and_chap'], series_name, source_info['chap_name_url'])
    return volume_info
