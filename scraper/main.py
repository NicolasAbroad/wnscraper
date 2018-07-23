#! python3
# main.py - Web novel scraper used to make ebooks separated by volume.
# Currently only supports syosetu.com

import io
import zipfile

from check_url import check_url

from get_info import generate_info
from get_info import parse_info
from get_info import query_info

from create_epub import chapters
from create_epub import container
from create_epub import content
from create_epub import folders
from create_epub import mimetype
from create_epub import nav
from create_epub import stylesheet
from create_epub import template
from create_epub import toc


def get_source(input_url):
    source = check_url.input_url_source_check(input_url)
    return source


def get_info(input_url, source):
    toc_html = query_info.get_page_html(input_url)
    uid = generate_info.random_uid()

    source_info = parse_info.original_source_info()

    series_name = query_info.get_string(toc_html, source_info[source]['html']['series_name'])
    author_name = query_info.get_string(toc_html, source_info[source]['html']['author_name'])
    author_name = parse_info.format_author(source, author_name)

    # Unable to factorize
    if query_info.volumes_exist(query_info.get_index_children(query_info.get_index(toc_html, source_info[source]['html']['html_index'])), source_info[source]['html']['vol_and_chap']):
        volume_info = query_info.scrape_chapter_info_by_volume(query_info.get_index_children(query_info.get_index(toc_html, source_info[source]['html']['html_index'])), source_info[source]['html']['vol_and_chap'], source_info[source]['html']['chap_name_url'])
    else:
        volume_info = query_info.get_dict_key(series_name)
        volume_info = query_info.scrape_all_chapter_info(volume_info, query_info.get_index_children(query_info.get_index(toc_html, source_info[source]['html']['html_index'])), source_info[source]['html']['vol_and_chap'], series_name, source_info[source]['html']['chap_name_url'])

    volume_names = {}
    for index, volume in enumerate(list(volume_info.keys())):
        volume_names[volume] = ('{0:02d}'.format(index+1) + ' - ' + volume, '{0:02d}'.format(index+1) + '%20-%20' + volume.replace(' ', '%20'))

    source_info['input_url'] = input_url
    source_info['source'] = source
    source_info[source]['info'] = {'series_name': series_name,
                            'author_name': author_name,
                            'volume_info': volume_info,
                            'volume_names': volume_names,
                            'uid': uid,
                            'request_id': 'PLACEHOLDER'}
    return source_info


def generate_all_volumes_to_disk(source_info):
    input_url = source_info['input_url']
    source = source_info['source']
    series_name = source_info[source]['info']['series_name']
    author_name = source_info[source]['info']['author_name']
    volume_names = source_info[source]['info']['volume_names']
    volume_info = source_info[source]['info']['volume_info']
    uid = source_info[source]['info']['uid']

    folders.create_series_folder(series_name)

    for i, volume in enumerate(volume_names.keys()):
#        if i == 1:                              # Used for testing
#            break
        volume_formatted_name = '{0:02d}'.format(i+1) + ' - ' + volume
        volume_chapters = volume_info[volume]

        epub_file_name = volume_formatted_name + '.epub'
        epub = zipfile.ZipFile('./download/{}/{}'.format(series_name, epub_file_name), 'w')
        mimetype.create_mimetype(epub)
        container.create_container(epub)
        toc_string = toc.create_toc(uid, volume_formatted_name)
        content_string_first_half = content.create_content(volume_formatted_name, author_name, uid)
        content_string_second_half = content.create_middle()

        for j, (tuple_ch_name, tuple_ch_url) in enumerate(volume_chapters):
            chapter_url = chapters.format_chapter_url(source_info[source]['html']['url_regex'], tuple_ch_url, input_url)
            chapter_html = query_info.get_page_html(chapter_url)
            chapter_number = chapters.chapter_get_text_for_element(chapter_html, source_info[source]['html']['chapter_number'])
            chapter_text = chapters.chapter_get_text_for_element(chapter_html, source_info[source]['html']['chapter_text'])
            chapter_complete = chapters.combine_name_and_text(chapter_number, chapter_text)

            xhtml_name = 'chap' + str(j)
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

    print('All files completed!')


def generate_all_volumes_to_memory(memory_file, source_info):
    input_url = source_info['input_url']
    source = source_info['source']
    series_name = source_info[source]['info']['series_name']
    author_name = source_info[source]['info']['author_name']
    volume_names = source_info[source]['info']['volume_names']
    volume_info = source_info[source]['info']['volume_info']
    uid = source_info[source]['info']['uid']

    buffer_all = io.BytesIO()
    all_volumes = zipfile.ZipFile(buffer_all, 'w')

    for i, volume in enumerate(volume_names.keys()):
#        if i == 1:
#            break
        volume_formatted_name = '{0:02d}'.format(i+1) + ' - ' + volume
        volume_chapters = volume_info[volume]

        epub_file_name = volume_formatted_name + '.epub'
        buffer_single = io.BytesIO()
        epub = zipfile.ZipFile(buffer_single, 'w')

        mimetype.create_mimetype(epub)
        container.create_container(epub)
        toc_string = toc.create_toc(uid, volume_formatted_name)
        content_string_first_half = content.create_content(volume_formatted_name, author_name, uid)
        content_string_second_half = content.create_middle()

        for j, (tuple_ch_name, tuple_ch_url) in enumerate(volume_chapters):
            chapter_url = chapters.format_chapter_url(source_info[source]['html']['url_regex'], tuple_ch_url, input_url)
            chapter_html = query_info.get_page_html(chapter_url)
            chapter_number = chapters.chapter_get_text_for_element(chapter_html, source_info[source]['html']['chapter_number'])
            chapter_text = chapters.chapter_get_text_for_element(chapter_html, source_info[source]['html']['chapter_text'])
            chapter_complete = chapters.combine_name_and_text(chapter_number, chapter_text)

            xhtml_name = 'chap' + str(j)
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
        buffer_single.seek(0)
        all_volumes.writestr(epub_file_name, buffer_single.read())
        buffer_single.close()
        print('Completed: ' + volume_formatted_name)

    all_volumes.close()
    return buffer_all


def generate_single_volume_to_disk(source_info, volume_name):
    input_url = source_info['input_url']
    source = source_info['source']
    series_name = source_info[source]['info']['series_name']
    author_name = source_info[source]['info']['author_name']
    volume_names = source_info[source]['info']['volume_names']
    volume_info = source_info[source]['info']['volume_info']
    uid = source_info[source]['info']['uid']

    folders.create_series_folder(series_name)

    volume_formatted_name = volume_names[volume_name][0]
    volume_chapters = volume_info[volume_name]

    epub_file_name = volume_formatted_name + '.epub'
    epub = zipfile.ZipFile('./download/{}/{}'.format(series_name, epub_file_name), 'w')
    mimetype.create_mimetype(epub)
    container.create_container(epub)
    toc_string = toc.create_toc(uid, volume_formatted_name)
    content_string_first_half = content.create_content(volume_formatted_name, author_name, uid)
    content_string_second_half = content.create_middle()

    for j, (tuple_ch_name, tuple_ch_url) in enumerate(volume_chapters):
        chapter_url = chapters.format_chapter_url(source_info[source]['html']['url_regex'], tuple_ch_url, input_url)
        chapter_html = query_info.get_page_html(chapter_url)
        chapter_number = chapters.chapter_get_text_for_element(chapter_html, source_info[source]['html']['chapter_number'])
        chapter_text = chapters.chapter_get_text_for_element(chapter_html, source_info[source]['html']['chapter_text'])
        chapter_complete = chapters.combine_name_and_text(chapter_number, chapter_text)

        xhtml_name = 'chap' + str(j)
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


def generate_single_volume_to_memory(memory_file, source_info, volume_name):
    input_url = source_info['input_url']
    source = source_info['source']
    series_name = source_info[source]['info']['series_name']
    author_name = source_info[source]['info']['author_name']
    volume_names = source_info[source]['info']['volume_names']
    volume_info = source_info[source]['info']['volume_info']
    uid = source_info[source]['info']['uid']

    volume_formatted_name = volume_names[volume_name][0]
    volume_chapters = volume_info[volume_name]

#    epub_file_name = volume_formatted_name + '.epub'
    epub = zipfile.ZipFile(memory_file, 'w')

    mimetype.create_mimetype(epub)
    container.create_container(epub)
    toc_string = toc.create_toc(uid, volume_formatted_name)
    content_string_first_half = content.create_content(volume_formatted_name, author_name, uid)
    content_string_second_half = content.create_middle()

    for j, (tuple_ch_name, tuple_ch_url) in enumerate(volume_chapters):
        chapter_url = chapters.format_chapter_url(source_info[source]['html']['url_regex'], tuple_ch_url, input_url)
        chapter_html = query_info.get_page_html(chapter_url)
        chapter_number = chapters.chapter_get_text_for_element(chapter_html, source_info[source]['html']['chapter_number'])
        chapter_text = chapters.chapter_get_text_for_element(chapter_html, source_info[source]['html']['chapter_text'])
        chapter_complete = chapters.combine_name_and_text(chapter_number, chapter_text)

        xhtml_name = 'chap' + str(j)
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
    return memory_file


#input_url = 'https://ncode.syosetu.com/n7103ev/'   # short volume
#input_url = 'https://ncode.syosetu.com/n1850ew/'   # short no volume
#input_url = 'https://ncode.syosetu.com/n7975cr/'   # くも
#input_url = 'https://ncode.syosetu.com/n8611bv/'   # ありふり

#source = get_source(input_url)
#volume_name = '１章：主役になりたくて'
#source_info = get_info(input_url, source)
#generate_all_volumes_to_disk(source_info)
#generate_single_volume_to_disk(source_info, volume_name)
