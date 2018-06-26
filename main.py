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

def input_url_source_check(input_url):                                               # Check source
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
        

def series(soup, input_url_source):
    if input_url_source == 'syosetu':
        return soup.select('.novel_title')[0].getText()                 # Series name

def author(soup, input_url_source):
    if input_url_source == 'syosetu':
        for data in soup.find_all('div', class_='novel_writername'):
            return data.text.lstrip()[3:-2]                             # Author's name

def chapter_names_and_urls(soup, input_url_source):
    if input_url_source == 'syosetu':
        index = soup.find('div', class_='index_box')
        index_sub_tags = index.children
        url_dict = {}
        volume = ''
        for sub_tag in index_sub_tags:
            sub_tag_str = str(sub_tag.encode('utf-8'))
            if 'chapter_title' in sub_tag_str:
                url_dict.setdefault(sub_tag.string, [])
                volume = sub_tag.string
            elif 'subtitle' in sub_tag_str:
                if volume == '':
                    volume = series(soup)
                    url_dict.setdefault(series(soup), [])
                url_dict[volume] += [(sub_tag.find('a').text, sub_tag.a['href'])]
        return url_dict

def create_essential_files(epub_file):
    epub_file.writestr('mimetype', 'application/epub+zip')

    epub_file.writestr('META-INF/container.xml', '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>''')

def toc_create_start(uid, volume_title):          # Creates start of toc.ncx string
    toc_string = '''<?xml version="1.0" encoding="UTF-8"?>
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
        <head>
            <meta name="dtb:uid" content="''' + uid + '''"/>
            <meta name="dtb:depth" content="1"/>
            <meta name="dtb:totalPageCount" content="0"/>
                <meta name="dtb:maxPageNumber" content="0"/>
        </head>
        <docTitle>
        <text>''' + volume_title + '''</text>
        </docTitle>
        <navMap>'''
    return toc_string

def toc_add_nav(toc_string, xhtml_name, order):      # Adds one nav point to toc.ncx string
    toc_string += '\n' + '''<navPoint id="''' + xhtml_name + '''" playOrder ="''' + str(order) + '''">
            <navLabel>
                <text>"''' + xhtml_name + '''"</text>
            </navLabel>
        <content src="''' + xhtml_name + '''.xhtml"/>
        </navPoint>'''
    return toc_string

def toc_finish(toc_string, epub_file):                     # Adds final lines to toc.ncx string and creates file
    toc_string += '\n</navMap>\n</ncx>'
    epub_file .writestr('OEBPS/toc.ncx', toc_string)

def content_create_start(volume_title, author_name, uid):         # Creates start of content.opf string
    content_string = '''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0" >
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>''' + volume_title + '''</dc:title>
        <dc:creator opf:role="aut">''' + author_name + '''</dc:creator>
        <dc:language>ja-JP </dc:language>
        <dc:rights>Public Domain</dc:rights>
        <dc:publisher>Nicolas</dc:publisher>
        <dc:identifier id="BookID" opf:scheme="UUID">''' + uid + '''</dc:identifier>
    </metadata>
    <manifest >
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="style" href="stylesheet.css" media-type="text/css"/>
        <item id="pagetemplate" href="page-template.xpgt" media-type="application/vnd.adobe-page-template+xml"/>''' + '\n'
    return content_string

def content_add_item_id(content_string, xhtml_name):              # Adds one item id to content.opf string
    content_string += '        <item id ="' + xhtml_name + '" href="' + xhtml_name + '.xhtml" media-type="application/xhtml+xml" />\n'
    return content_string

def content_create_middle():                          # Finishes manifest section and starts spine section in content.opf string
    content_string = '    </manifest>\n    <spine  toc="ncx">\n'
    return content_string

def content_add_itemref(content_string, xhtml_name):                            # Adds one itemref to content.opf string
    content_string += '        <itemref idref ="' + xhtml_name + '" />\n'
    return content_string

def content_finish(content_string, epub_file):                                 # Adds final lines to content.opf string and creates file
    content_string += '    </spine>\n</package>'
    epub_file.writestr('OEBPS/content.opf', content_string)

def stylesheet_create(epub_file):
    style = '''body { margin-left: 5%; margin-right: 5%; margin-top: 5%; margin-bottom: 5%; text-align: justify; }
pre { font-size: x-small; }
h1 { text-align: center; }
h2 { text-align: center; }
h3 { text-align: center; }
h4 { text-align: center; }
.CI {
    text-align:center;
    margin-top:0px;
    margin-bottom:0px;
    padding:0px;
    }
'''
    epub_file.writestr('OEBPS/stylesheet.css', style)

def template_create(epub_file):
    template = '''<ade:template xmlns="http://www.w3.org/1999/xhtml" xmlns:ade="http://ns.adobe.com/2006/ade"
         xmlns:fo="http://www.w3.org/1999/XSL/Format">

  <fo:layout-master-set>
   <fo:simple-page-master master-name="single_column">
        <fo:region-body margin-bottom="3pt" margin-top="0.5em" margin-left="3pt" margin-right="3pt"/>
    </fo:simple-page-master>
  
    <fo:simple-page-master master-name="single_column_head">
        <fo:region-before extent="8.3em"/>
        <fo:region-body margin-bottom="3pt" margin-top="6em" margin-left="3pt" margin-right="3pt"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="two_column"    margin-bottom="0.5em" margin-top="0.5em" margin-left="0.5em" margin-right="0.5em">
        <fo:region-body column-count="2" column-gap="10pt"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="two_column_head" margin-bottom="0.5em" margin-left="0.5em" margin-right="0.5em">
        <fo:region-before extent="8.3em"/>
        <fo:region-body column-count="2" margin-top="6em" column-gap="10pt"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="three_column" margin-bottom="0.5em" margin-top="0.5em" margin-left="0.5em" margin-right="0.5em">
        <fo:region-body column-count="3" column-gap="10pt"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="three_column_head" margin-bottom="0.5em" margin-top="0.5em" margin-left="0.5em" margin-right="0.5em">
        <fo:region-before extent="8.3em"/>
        <fo:region-body column-count="3" margin-top="6em" column-gap="10pt"/>
    </fo:simple-page-master>

    <fo:page-sequence-master>
        <fo:repeatable-page-master-alternatives>
            <fo:conditional-page-master-reference master-reference="three_column_head" page-position="first" ade:min-page-width="80em"/>
            <fo:conditional-page-master-reference master-reference="three_column" ade:min-page-width="80em"/>
            <fo:conditional-page-master-reference master-reference="two_column_head" page-position="first" ade:min-page-width="50em"/>
            <fo:conditional-page-master-reference master-reference="two_column" ade:min-page-width="50em"/>
            <fo:conditional-page-master-reference master-reference="single_column_head" page-position="first" />
            <fo:conditional-page-master-reference master-reference="single_column"/>
        </fo:repeatable-page-master-alternatives>
    </fo:page-sequence-master>

  </fo:layout-master-set>

  <ade:style>
    <ade:styling-rule selector=".title_box" display="adobe-other-region" adobe-region="xsl-region-before"/>
  </ade:style>

</ade:template>'''
    epub_file.writestr('OEBPS/page-template.xpgt', template)

def chapter_get_string(url):                                        # Change argument to extracted chapter url list
    if input_url_source == 'syosetu':
        r = requests.get(url)
        r.raise_for_status()
        page = bs4.BeautifulSoup(r.content, "html.parser")

        chapter_number = page.find('div', attrs={'id':'novel_no'})
        chapter_number = chapter_number.text

        chapter_string = page.find('div', attrs={'id':'novel_honbun'})
        chapter_string = chapter_string.text
        chapter_string = chapter_string.strip()
        chapter_string = chapter_number + '\n\n' + chapter_string
        chapter_string = chapter_string.replace('\n', '</p>\n<p>')
        return chapter_string

def chapter_create_file(chapter_title, chapter_string, xhtml_name, epub_file):
    chapter_head = '''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>''' + chapter_title + '''</title>
</head>
<body>''' + '\n<h3>' + chapter_title + '</h3>\n<p> '
    chapter_complete = chapter_head + chapter_string + '</p>\n</body>\n</html>'
    epub_file.writestr('OEBPS/' + xhtml_name + '.xhtml', chapter_complete)


#input_url = 'https://ncode.syosetu.com/n7975cr/'                    # Change to user input
input_url = 'https://ncode.syosetu.com/n8611bv/'                    # Change to user input
input_url_source = input_url_source_check(input_url)
res = requests.get(input_url)
res.raise_for_status()
toc = bs4.BeautifulSoup(res.content, "html.parser")
rand = 'nicolas' + str(random.randint(100000000000,999999999999))   # Random string for id

series_name = series(toc, input_url_source)
author_name = author(toc, input_url_source)
volume_names = list(chapter_names_and_urls(toc, input_url_source).keys())
chapter = chapter_names_and_urls(toc, input_url_source)

for i, volume in enumerate(volume_names):
#    if i == 1:                                                     # Test on the first volume of inputted url
#        sys.exit()
    volume_formatted_name = '{0:02d}'.format(i+1) + ' - ' + volume
    epub_file_name = volume_formatted_name + '.epub'
    epub = zipfile.ZipFile(epub_file_name, 'w')

    create_essential_files(epub)
    
    toc_string = toc_create_start(rand,volume_formatted_name)

    content_string_first_half = content_create_start(volume_formatted_name, author_name, rand)
    content_string_second_half = content_create_middle()

    volume_chapters = chapter_names_and_urls(toc, input_url_source)[volume]
    j = 1
    for tuple in range(len((volume_chapters))):
        chapter_url_end_unformatted = re.compile(r'\d+/$').findall(volume_chapters[tuple][1])
        chapter_url_end_formatted = chapter_url_end_unformatted[0][:-1]
        chapter_url = input_url + chapter_url_end_formatted
        chapter_string = chapter_get_string(chapter_url)
        xhtml_name = 'chap' + str(j)
        chapter_create_file(volume_chapters[tuple][0], chapter_string, xhtml_name, epub)
        toc_string = toc_add_nav(toc_string, xhtml_name, tuple)
        
        content_string_first_half = content_add_item_id(content_string_first_half, xhtml_name)
        content_string_second_half = content_add_itemref(content_string_second_half, xhtml_name)

        j += 1

    toc_finish(toc_string, epub)
    content_string = content_string_first_half + content_string_second_half
    content_finish(content_string, epub)
    stylesheet_create(epub)
    template_create(epub)
    epub.close()
    print('Completed: ' + volume_formatted_name)

input('All files completed!\nPress enter to exit.')
