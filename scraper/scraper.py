#! python3
# scraper.py - Web novel scraper used to make ebooks separated by volume.
# Currently only supports syosetu.com

from app import app
import io
import logging
import zipfile
from check_url import check_url
from get_info import generate_info, parse_info, query_info
from create_epub import chapters, container, content, folders, mimetype, nav, stylesheet, template, toc


logger = logging.getLogger(__name__)
#logger = logging.getLogger('wnscraper')


def check_source(input_url):
    source = check_url.input_url_source_check(input_url)
    if source:
        app.logger.debug('Scraper - Source url: %s' % source)
    else:
        app.logger.warn('Scraper - Invalid url inputted')
    return source


def get_info(input_url, source):
    toc_html = query_info.get_page_html(input_url)
    uid = generate_info.random_uid()

    source_info = parse_info.original_source_info()

    series_name = query_info.get_string(toc_html, source_info[source]['html']['series_name'])
    author_name = query_info.get_string(toc_html, source_info[source]['html']['author_name'])
    author_name = parse_info.format_author(source, author_name)

    # Unable to factorize
#    if query_info.volumes_exist(query_info.get_index_children(query_info.get_index(toc_html, source_info[source]['html']['html_index'])), source_info[source]['html']['vol_and_chap']):
#        volume_info = query_info.scrape_chapter_info_by_volume(query_info.get_index_children(query_info.get_index(toc_html, source_info[source]['html']['html_index'])), source_info[source]['html']['vol_and_chap'], source_info[source]['html']['chap_name_url'])
    html_index_id = source_info[source]['html']['html_index']
    vol_and_chap_id = source_info[source]['html']['vol_and_chap']
    chap_name_url_id = source_info[source]['html']['chap_name_url']
    
    index = query_info.get_index(toc_html, html_index_id)
    index_children = query_info.get_index_children(index)
    
    if query_info.volumes_exist(index_children, vol_and_chap_id):
        volume_info = query_info.scrape_chapter_info_by_volume(query_info.get_index_children(index), vol_and_chap_id, chap_name_url_id)

    else:
        volume_info = query_info.get_dict_key(series_name)
        volume_info = query_info.scrape_all_chapter_info(volume_info, query_info.get_index_children(query_info.get_index(toc_html, source_info[source]['html']['html_index'])), source_info[source]['html']['vol_and_chap'], series_name, source_info[source]['html']['chap_name_url'])

#    volume_names = parse_info.extract_volume_names_and_numbers(volume_info)
    volume_names = parse_info.extract_volume_names(query_info.get_index_children(index), vol_and_chap_id)
#    info = volume_info['info']
#    volume_names = volume_info['names']

    source_info['input_url'] = input_url
    source_info['source'] = source
    source_info[source]['info'] = {'series_name': series_name,
                            'author_name': author_name,
                            'volume_info':volume_info,
                            'volume_names': volume_names,
                            'uid': uid,
                            'request_id': 'PLACEHOLDER'}
    app.logger.debug('Scraper - Source info retrieved')
    app.logger.debug('%s' % source_info)
    return source_info


def create_source_info(input_url):
    source = check_source(input_url)
    source_info = get_info(input_url, source)
    return source_info


def generate_all_volumes_to_disk(source_info):
    input_url = parse_info.retrieve_input_url_from(source_info)
    source = parse_info.retrieve_source_from(source_info)
    series_name = parse_info.retrieve_series_name_from(source_info)
    author_name = parse_info.retrieve_author_name_from(source_info)
    volume_names = parse_info.retrieve_volume_names_from(source_info)
    volume_info = parse_info.retrieve_volume_info_from(source_info)
    uid = parse_info.retrieve_uid_from(source_info)

    folders.create_series_folder(series_name)

    for volume_number in volume_names.keys():
#        if i == 1:
#            break
        volume_name = volume_names[volume_number]
        volume_formatted_name = parse_info.format_volume_name(volume_number, volume_name)
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

    print('All files completed!')


def generate_all_volumes_to_memory(memory_file, source_info):
    input_url = parse_info.retrieve_input_url_from(source_info)
    source = parse_info.retrieve_source_from(source_info)
    series_name = parse_info.retrieve_series_name_from(source_info)
    author_name = parse_info.retrieve_author_name_from(source_info)
    volume_names = parse_info.retrieve_volume_names_from(source_info)
    volume_info = parse_info.retrieve_volume_info_from(source_info)
    uid = parse_info.retrieve_uid_from(source_info)

    buffer_all = io.BytesIO()
    all_volumes = zipfile.ZipFile(buffer_all, 'w')

    for volume_number in volume_names.keys():
#        if i == 1:
#            break
        volume_name = volume_names[volume_number]
        volume_formatted_name = parse_info.format_volume_name(volume_number, volume_name)
        volume_chapters = volume_info[volume_name]

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

    all_volumes.close()
    app.logger.debug('Scraper - All volumes written to memory - Series: %s' % series_name)
    return buffer_all


def generate_single_volume_to_disk(source_info, volume_number):
    input_url = parse_info.retrieve_input_url_from(source_info)
    source = parse_info.retrieve_source_from(source_info)
    series_name = parse_info.retrieve_series_name_from(source_info)
    author_name = parse_info.retrieve_author_name_from(source_info)
    volume_names = parse_info.retrieve_volume_names_from(source_info)
    volume_info = parse_info.retrieve_volume_info_from(source_info)
    uid = parse_info.retrieve_uid_from(source_info)

    folders.create_series_folder(series_name)

    volume_name = volume_names[volume_number]
    volume_formatted_name = parse_info.format_volume_name(volume_number, volume_name)

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


def generate_single_volume_to_memory(memory_file, source_info, volume_number):
    input_url = parse_info.retrieve_input_url_from(source_info)
    source = parse_info.retrieve_source_from(source_info)
    series_name = parse_info.retrieve_series_name_from(source_info)
    author_name = parse_info.retrieve_author_name_from(source_info)
    volume_names = parse_info.retrieve_volume_names_from(source_info)
    volume_info = parse_info.retrieve_volume_info_from(source_info)
    uid = parse_info.retrieve_uid_from(source_info)

    volume_name = volume_names[volume_number]
    volume_formatted_name = parse_info.format_volume_name(volume_number, volume_name)
    volume_chapters = volume_info[volume_name]

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
    app.logger.debug('Scraper - One volume written to memory - Series: %s - Volume name: %s' % (series_name, volume_name))
    return memory_file


if __name__ == '__main__':
    input_url = input('Please input a url address: ')
    source_info = create_source_info(input_url)
    generate_all_volumes_to_disk(source_info)
