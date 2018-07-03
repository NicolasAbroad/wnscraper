#! python3
# epub_scraper.py - Scrapes content from syosetu.com to make ebooks,
# separated by volume.

import requests
import bs4
import os
import shutil
import zipfile
import random
import re
import sys

import chapters
import content
import essential_files
import nav
import stylesheet
import scraper
import template
import toc

#input_url = 'https://ncode.syosetu.com/n7975cr/'                    # Change to user input
input_url = 'https://ncode.syosetu.com/n8611bv/'            # Change to user input
source = scraper.input_url_source_check(input_url)
toc_html = scraper.get_page_html(input_url)
rand = 'nicolas' + str(random.randint(100000000000,999999999999))   # Random string for uid

source_info = {'syosetu':{'series_name': ('p', 'novel_title'),
                 'author_name': ('div', 'novel_writername'),
                 'html_index': ('div', 'index_box'),
                 'volume': ('div', 'class', 'chapter_title'),
                 'vol_and_chap': ('chapter_title', 'subtitle'),
                 'chap_name_url': ('a', 'href'),
                 'chapter_number': ('div', 'id', 'novel_no'),
                 'chapter_text': ('div', 'id', 'novel_honbun'),
                 'url_regex': r'\d+/$'}}

series_name = scraper.scrape_string(toc_html, source_info[source]['series_name'])
author_name = scraper.scrape_string(toc_html, source_info[source]['author_name'])[4:-1]      # Include string removal in function

# Querying info twice
if scraper.volumes_exist(scraper.get_index_children(scraper.get_index(toc_html, source_info[source]['html_index'])), source_info[source]['vol_and_chap']):
    volume_info = scraper.scrape_chapter_info_by_volume(scraper.get_index_children(scraper.get_index(toc_html, source_info[source]['html_index'])), source_info[source]['vol_and_chap'], source_info[source]['chap_name_url'])
else:
    volume_info = scraper.get_dict_key(series_name)
    volume_info = scraper.scrape_chapter_info_by_chapter(volume_info, scraper.get_index_children(scraper.get_index(toc_html, source_info[source]['html_index'])), source_info[source]['vol_and_chap'], series_name, source_info[source]['chap_name_url'])

volume_names = list(volume_info.keys())

for i, volume in enumerate(volume_names):
#    if i == 2:                              # Used for testing
#        sys.exit()
    volume_formatted_name = '{0:02d}'.format(i+1) + ' - ' + volume
    volume_chapters = volume_info[volume]

    epub_file_name = volume_formatted_name + '.epub'
    epub = zipfile.ZipFile(epub_file_name, 'w')
    essential_files.create_essentials(epub)
    toc_string = toc.create_toc(rand, volume_formatted_name)
    content_string_first_half = content.create_content(volume_formatted_name, author_name, rand)
    content_string_second_half = content.create_middle()

    for j, (tuple_ch_name, tuple_ch_url) in enumerate(volume_chapters):
        chapter_url = chapters.format_chapter_url(source_info[source]['url_regex'], tuple_ch_url, input_url)
        chapter_html = scraper.get_page_html(chapter_url)
        chapter_number = scraper.chapter_get_element_text(chapter_html, source_info[source]['chapter_number'])
        chapter_text = scraper.chapter_get_element_text(chapter_html, source_info[source]['chapter_text'])
        chapter_complete = scraper.chapter_truncate_name_to_string(chapter_number, chapter_text)
        chapter_complete = scraper.chapter_string_replace_broken_characters(chapter_complete)

        xhtml_name = 'chap' + str(j + 1)

        chapters.create_chapter(tuple_ch_name, chapter_complete, xhtml_name, epub)
        toc_string = toc.add_nav(toc_string, xhtml_name, str(j))
        content_string_first_half = content.add_item_id(content_string_first_half, xhtml_name)
        content_string_second_half = content.add_itemref(content_string_second_half, xhtml_name)

    toc.finish_toc(toc_string, epub)
    content_string = content_string_first_half + content_string_second_half
    content.finish_content(content_string, epub)
    stylesheet.create_stylesheets(epub)
    nav.create_nav(epub)
    template.create_template(epub)
    epub.close()
    print('Completed: ' + volume_formatted_name)

input('All files completed!\nPress enter to exit.')
