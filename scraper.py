# scraper.py - Scrapes information from syosetu.com
import bs4
import re
import requests

def input_url_source_check(input_url):
    sources_regex = {'syosetu': '((http:\/\/|https:\/\/)?(ncode.syosetu.com\/n))(\d{4}[a-z]{2}\/?)$'}
    for key in sources_regex:
        regex = re.compile(sources_regex[key])
        if re.match(regex, input_url):
            return key
        else:
            raise ValueError('Please input URL correctly.')
            input()
            sys.exit()

def get_page_html(url):
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.content, "html.parser")
    return soup

# Use to get serie's name and author
def scrape_string(soup, html_element):
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

# Use if volumes don't exist
def get_dict_key(series_name):
    chapter_info_dict = {}
    chapter_info_dict.setdefault(series_name, [])
    return chapter_info_dict

# Use if volumes don't exist
def scrape_chapter_info_by_chapter(chapter_info_dict, index_children, name_element, series_name, target_info_element):
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

# Use if volumes don't exist
def scrape_chapter_info_by_volume(index_children, name_element, target_info_element):
    def inner(index_children, name_element, target_info_element):
        chapter_info_dict = {}
        volume = ''
        for index_child in index_children:
            index_child_str = str(index_child)
            if name_element[0] in index_child_str:
                volume = index_child.string
                chapter_info_dict.setdefault(volume, [])         # index_child_str = volume name
            elif name_element[1] in index_child_str:
                ch_name = index_child.find(target_info_element[0])
                chapter_info_dict[volume] += [(ch_name.text, ch_name.attrs[target_info_element[1]])]
        return chapter_info_dict
    return inner(index_children, name_element, target_info_element)

# (page, find_element)? find_element = 'element_name, attrs={attribute_key:attribute_value}'
def chapter_get_element_text(page, element_name):
    chapter_element = page.find(element_name[0], attrs={element_name[1]:element_name[2]})
    chapter_element = chapter_element.text.strip()
    return chapter_element

def chapter_truncate_name_to_string(chapter_number, chapter_string):
    chapter_string = chapter_number + '\n\n' + chapter_string
    return chapter_string

def chapter_string_replace_broken_characters(chapter_string):
    replace_dict = {'"': '&quot;', '&': '&quot;', '<': '&lt;', '>': '&gt;','\n': '</p>\n<p>'}
    for key in replace_dict:
        chapter_string = chapter_string.replace(key, replace_dict[key])
    return chapter_string
