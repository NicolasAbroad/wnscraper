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

def series(soup):
    return soup.select('.novel_title')[0].getText()                 # Series name

def author(soup):
    for data in soup.find_all('div', class_='novel_writername'):
        return data.text.lstrip()[3:-2]                             # Author's name

def chapter_names_and_urls(soup):
    index = soup.find('div', class_='index_box')
    children = index.children
    url_dict = {}
    volume = 0
    for child in children:
        if 'chapter_title' in str(child.encode('utf-8')):
            url_dict.setdefault(child.string, [])
            volume = child.string
        elif 'subtitle' in str(child.encode('utf-8')):
            url_dict[volume] += [(child.find('a').text, child.a['href'])]
    return url_dict

def create_folders(volume_name):                # Enters volume directory
    try:
        os.makedirs(volume_name)
    except FileExistsError:
        pass
    os.chdir('.\\' + volume_name)               
    try:
        os.makedirs('META-INF')
    except FileExistsError:
        pass
    try:
        os.makedirs('OEBPS')
    except FileExistsError:
        pass

def create_essential_files():
    # Create mimetype in root folder
    mimetype = open('mimetype', 'w')
    mimetype.write('application/epub+zip')
    mimetype.close()
    # Create container.xml in META-INF folder
    os.chdir('.\\META-INF')
    container = open('container.xml', 'w')
    container.write('''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>''')
    container.close()
    os.chdir('..\\')

def toc_create_start(uid, volume_name):          # Creates start of toc.ncx string
    toc_string = '''<?xml version="1.0" encoding="UTF-8"?>
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
        <head>
            <meta name="dtb:uid" content="''' + uid + '''"/>
            <meta name="dtb:depth" content="1"/>
            <meta name="dtb:totalPageCount" content="0"/>
                <meta name="dtb:maxPageNumber" content="0"/>
        </head>
        <docTitle>
        <text>''' + volume_name + '''</text>
        </docTitle>'''
    return toc_string

def toc_add_nav(toc_string, chapter_name, order):      # Adds one nav point to toc.ncx string
    toc_string += '\n' + '''<navMap>
        <navPoint id="''' + chapter_name + '''" playOrder ="''' + str(order) + '''">
            <navLabel>
                <text>"''' + chapter_name + '''"</text>
            </navLabel>
        <content src="''' + chapter_name + '''.xhtml "/>
    </navPoint>'''
    return toc_string

def toc_finish(toc_string):                     # Adds final lines to toc.ncx string and creates file
    toc_string += '\n</navMap>\n</ncx>'
    os.chdir('.\\OEBPS')
    toc_file = open('toc.ncx', mode='w')
    toc_file.write(toc_string)
    toc_file.close()
    os.chdir('..\\')

def content_create_start(volume_name, author_name, uid):         # Creates start of content.opf string
    content_string = '''<?xml version="1.0" encoding="UTF-8"??>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0" >
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>''' + volume_name + '''</dc:title>
        <dc:creator opf:role="aut">''' + author_name + '''</dc:creator>
        <dc:language>ja-JP </dc:language>
        <dc:rights>Public Domain</dc:rights>
        <dc:publisher>Nicolas</dc:publisher>
        <dc:identifier id="BookID" opf:scheme="UUID">''' + uid + '''</dc:identifier>
    </metadata>
    <manifest >
        <item id="ncx" href="toc.ncx " media-type="application/x-dtbncx+xml" />
        <item id="style" href="stylesheet.css" media-type="text/css" />
        <item id="pagetemplate" href="page-template.xpgt" media-type="application/vnd.adobe-page-template+xml" />''' + '\n'
    return content_string

def content_add_item_id(content_string, chapter_name):              # Adds one item id to content.opf string
    content_string += '        <item id ="' + chapter_name + '" href="' + chapter_name + '.xhtml" media-type="application/xhtml+xml" />\n'
    return content_string

def content_create_middle():                          # Finishes manifest section and starts spine section in content.opf string
    content_string = '    </manifest>\n    <spine  toc="ncx">\n'
    return content_string

def content_add_itemref(content_string, chapter_name):                            # Adds one itemref to content.opf string
    content_string += '        <itemref idref ="' + chapter_name + '" />\n'
    return content_string

def content_finish(content_string):                                 # Adds final lines to content.opf string and creates file
    content_string += '    </spine>\n</package>'
    os.chdir('.\\OEBPS')
    content_file = open('content.opf', mode='w')
    content_file.write(content_string)
    content_file.close()
    os.chdir('..\\')

def chapter_get_string(url):                                        # Change argument to extracted chapter url list
    url = 'https://ncode.syosetu.com/n8611bv/1'                     # Change to input
    r = requests.get(url)
    r.raise_for_status()
    page = bs4.BeautifulSoup(r.content, "html.parser")
    chapter_string = str(page.find('div', attrs={'id':'novel_color'}))
    chapter_string = chapter_string.encode('utf-8')
    return chapter_string

def chapter_create_file(chapter_name, chapter_string):
    os.chdir('.\\OEBPS')
    chapter_file = open(chapter_name + '.xhtml', 'wb')
    chapter_head = '''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title></title>
</head>
<body>''' + '\n'
    chapter_head = chapter_head.encode('utf-8')
    chapter_file.write(chapter_head)
    chapter_file.write(chapter_string)
    chapter_file.write('</body>\n</html>'.encode('utf-8'))
    chapter_file.close()
    os.chdir('..\\')

def zip_create(volume_name):
    volume_zip = zipfile.ZipFile(volume_name + '.zip', 'w')                 # TODO: Add number in front of file name

def zip_add_files(volume_name, file_name, folder):
    for root, directory, files in os.walk(folder):
        for file in files:
            volume_zip.write(file_name, compress_type=zipfile.ZIP_DEFLATED)

def zip_close(volume_name):
    volume_zip.close()


input_url = 'https://ncode.syosetu.com/n8611bv/'                    # Change to user input
res = requests.get(input_url)
res.raise_for_status()
toc = bs4.BeautifulSoup(res.content, "html.parser")
rand = 'nicolas' + str(random.randint(100000000000,999999999999))   # Random string for id

series_name = series(toc)
author_name = author(toc)
volume_names = list(chapter_names_and_urls(toc).keys())
chapter = chapter_names_and_urls(toc)

for i, volume in enumerate(volume_names):
    volume_formatted_name = '{0:02d}'.format(i+1) + ' - ' + volume
    create_folders(volume_formatted_name)
    create_essential_files()

    toc_string = toc_create_start(rand,volume_formatted_name)

    content_string_first_half = content_create_start(volume_formatted_name, author_name, rand)
    content_string_second_half = content_create_middle()

    volume_chapters = chapter_names_and_urls(toc)[volume]
    for tuple in range(len(volume_chapters)):
        chapter_url_end_unformatted = re.compile(r'\d+/$').findall(volume_chapters[tuple][1])
        chapter_url_end_formatted = chapter_url_end_unformatted[0][:-1]
        chapter_url = input_url + chapter_url_end_formatted
        chapter_string = chapter_get_string(chapter_url)
        chapter_create_file(volume_chapters[tuple][0], chapter_string)
        
        toc_string = toc_add_nav(toc_string, volume_chapters[tuple][0], tuple)
        
        content_string_first_half = content_add_item_id(content_string_first_half, volume_chapters[tuple][0])
        content_string_second_half = content_add_itemref(content_string_second_half, volume_chapters[tuple][0])
        
    toc_finish(toc_string)
    content_string = content_string_first_half + content_string_second_half
    content_finish(content_string)
    os.chdir('..\\')
    print('Completed: ' + volume_formatted_name)


'''    REFERENCE LOOP
for volume in volume_names:
    print(volume + ':')
    volume_chapters = chapter_names_and_urls(toc)[volume]
    for tuple in range(len(volume_chapters)):
        print(volume_chapters[tuple][0] + ': ' + volume_chapters[tuple][1])'''

# Get author name
# Get series name
# Get volume names and chapter names/urls
# TODO: If function for situation with no names
# TODO: For volume in volume names
    # Create mimetype, META-INF folder and OEBPS folder
    # Create head for content.opf and toc.ncx
    # TODO: Create bodies and spine for content.opf and toc.ncx
    # TODO: Get chapter urls in dict file
    # TODO: For url in chapter urls
        # TODO: Get chapter name
        # TODO: Append appropriate line to bodies and spine (content, toc)
        # Get xhtml content for every chapter
        # TODO: Create XHTML file
    # TODO: Complete toc.ncx and content.opf and join files
    # TODO: Create zip file
    # TODO: Add files to zip file
    # TODO: Change extension to epub

input()
