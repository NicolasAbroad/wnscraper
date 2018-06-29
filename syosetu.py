# syosetu.py - Scrapes information from syosetu.com
import requests
import bs4

class Scraper():
    def scrape_string(soup, html_element, html_class):
        for name in soup.find_all(html_element, class_=html_class):
            return name.text

    def get_index(soup, html_element, html_class):
        index = soup.find(html_element, class_=html_class)
        return index.children

#    def scrape_element():

    def scrape_index(index, name_element, series_name):
        name_url_dict = {}
        volume_name = ''
        for index_subheader in index:
            index_subheader = str(index_subheader.encode('utf-8'))
            # use tuple for name_element: ('chapter_title', 'subtitle')  --  Change depending on website
            if name_element[0] in index_subheader:                  # use get_index for index
                volume_name = index_subheader
                name_url_dict.setdefault(volume_name, [])
            elif name_element[1] in index_subheader:
                if volume_name == '':
                    volume_name = series_name                       # use scrape_string for series_name
                    name_url_dict.setdefault(series_name, [])
#                name_url_dict[volume_name] += []
                name_url_dict[volume_name] += [(sub_tag.find('a').text, sub_tag.a['href'])]
        return name_url_dict

def chapter_names_and_urls(soup, input_url_source):
    index = soup.find('div', class_='index_box')
    index_sub_tags = index.children
    url_dict = {}
    volume = ''
    for sub_tag in index_sub_tags:
        sub_tag_str = str(sub_tag.encode('utf-8'))
        if 'chapter_title' in sub_tag_str:
            volume = sub_tag.string
            url_dict.setdefault(volume, [])
        elif 'subtitle' in sub_tag_str:
            if volume == '':
                volume = series(soup)
                url_dict.setdefault(series(soup), [])
            url_dict[volume] += [(sub_tag.find('a').text, sub_tag.a['href'])]
    return url_dict

def chapter_get_string(url): # Change argument to extracted chapter url list
    r = requests.get(url)
    r.raise_for_status()
    page = bs4.BeautifulSoup(r.content, "html.parser")

    chapter_number = page.find('div', attrs={'id':'novel_no'})
    chapter_number = chapter_number.text

    chapter_string = page.find('div', attrs={'id':'novel_honbun'})
    chapter_string = chapter_string.text
    chapter_string = chapter_string.strip()
    chapter_string = chapter_number + '\n\n' + chapter_string
    return chapter_string

def chapter_string_check(chapter_string):
    replace_dict = {'"': '&quot;', '&': '&quot;', '<': '&lt;', '>': '&gt;','\n': '</p>\n<p>'}
    for key in replace_dict:
        chapter_string = chapter_string.replace(key, replace_dict[key])
    return chapter_string
