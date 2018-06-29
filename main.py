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
import syosetu
import template
from toc import *

def input_url_source_check(input_url):                                  # Check source
    syosetu_source = re.compile(r'''
                                ^((http:\/\/|https:\/\/)?
                                (ncode.syosetu.com\/n))
                                (\d{4}[a-z]{2}\/?)$''', re.X)
    if re.match(syosetu_source, input_url):
        return 'syosetu'
    else:
        raise ValueError('Please input URL correctly.')
        input()
        sys.exit()

#input_url = 'https://ncode.syosetu.com/n7975cr/'                    # Change to user input
input_url = 'https://ncode.syosetu.com/n8611bv/'                    # Change to user input
input_url_source = input_url_source_check(input_url)
res = requests.get(input_url)
res.raise_for_status()
toc = bs4.BeautifulSoup(res.content, "html.parser")
rand = 'nicolas' + str(random.randint(100000000000,999999999999))   # Random string for id

#series_name = syosetu.series(toc, input_url_source)
series_name = syosetu.Scraper.scrape_string(toc, 'p', 'novel_title')
#author_name = syosetu.author(toc, input_url_source)
author_name = syosetu.Scraper.scrape_string(toc, 'div', 'novel_writername')[4:-1]
volume_names = list(syosetu.chapter_names_and_urls(toc, input_url_source).keys())
chapter = syosetu.chapter_names_and_urls(toc, input_url_source)

for i, volume in enumerate(volume_names):
    if i == 1:                                                     # Test on the first volume of inputted url
        sys.exit()
    volume_formatted_name = '{0:02d}'.format(i+1) + ' - ' + volume
    epub_file_name = volume_formatted_name + '.epub'
    epub = zipfile.ZipFile(epub_file_name, 'w')

    essential_files.create_essentials(epub)

    toc_string = create_toc(rand, volume_formatted_name)

    content_string_first_half = content.create_content(volume_formatted_name, author_name, rand)
    content_string_second_half = content.create_middle()

    volume_chapters = syosetu.chapter_names_and_urls(toc, input_url_source)[volume]
    j = 1
    for tuple in range(len((volume_chapters))):
        chapter_url_end_unformatted = re.compile(r'\d+/$').findall(volume_chapters[tuple][1])
        chapter_url_end_formatted = chapter_url_end_unformatted[0][:-1]
        chapter_url = input_url + chapter_url_end_formatted
        chapter_string = syosetu.chapter_get_string(chapter_url)
        chapter_string = syosetu.chapter_string_check(chapter_string)
        xhtml_name = 'chap' + str(j)
        chapters.create_chapter(volume_chapters[tuple][0], chapter_string, xhtml_name, epub)
        toc_string = add_nav(toc_string, xhtml_name, tuple)
        
        content_string_first_half = content.add_item_id(content_string_first_half, xhtml_name)
        content_string_second_half = content.add_itemref(content_string_second_half, xhtml_name)

        j += 1

    finish_toc(toc_string, epub)
    content_string = content_string_first_half + content_string_second_half
    content.finish_content(content_string, epub)
    stylesheet.create_stylesheets(epub)
    nav.create_nav(epub)
    template.create_template(epub)
    epub.close()
    print('Completed: ' + volume_formatted_name)

input('All files completed!\nPress enter to exit.')
