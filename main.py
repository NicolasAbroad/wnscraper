#! python3
# epub_scraper.py - Scrapes content from syosetu.com to make ebooks,
# separated by volume.

import requests, bs4, os, shutil, zipfile, random

res = requests.get('https://ncode.syosetu.com/n8611bv/')            # Change to input
res.raise_for_status()
toc = bs4.BeautifulSoup(res.content, "html.parser")
rand = 'nicolas' + str(random.randint(100000000000,999999999999))   # Random string for id

def series(soup):
    return soup.select('.novel_title')[0].getText()                 # Series name

def author(soup):
    for data in soup.find_all('div', class_='novel_writername'):
        return data.text.lstrip()[3:-2]                             # Author's name

#for div in toc.find('div', class_='.character_title'):
#    print(len(title.find('div', class_='.subtitle')))

def book_title(soup):                                               # TBD - Obtain book titles and use in for loop
    book_title = []
    for book in range(len(soup.select('.chapter_title'))):
        book_title += soup.select('.chapter_title')[book]
    return book_title

def chapter_url(soup):
    chapter_urls = []
    for chapter in range(len(soup.select('.subtitle'))):
        chapter_urls += soup.select('.subtitle')[chapter].a['href']
        #return chapter_urls[c].text.strip()
        return chapter_urls                                         # TBD - Links broken

def head(soup):
    # Create folders
    if os.path.exists('.\\' + series(soup)):
        pass
    else:
        os.makedirs('.\\' + series(soup))

    os.chdir('.\\' + series(soup))

    if os.path.exists('.\\META-INF'):
        pass
    else:
        os.makedirs('.\\META-INF')
    if os.path.exists('.\\OEBPS'):
        pass
    else:
        os.makedirs('.\\OEBPS')

    # Create mimetype
    mimetype = open('mimetype', 'w')
    mimetype.write('application/epub+zip')
    mimetype.close()
    # Create container
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
    # Create first half of toc.ncx
    toc_head = open('toc_head', 'w')
    toc_head.write('''<?xml version="1.0" encoding="UTF-8"?>
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
          <head>
            <meta name="dtb:uid" content="''' + rand + '''"/>
            <meta name="dtb:depth" content="1"/>
            <meta name="dtb:totalPageCount" content="0"/>
            <meta name="dtb:maxPageNumber" content="0"/>
          </head>
          <docTitle>
            <text>''' + 'book_name' + '''</text>
          </docTitle>''')                               # Book name TBD
    toc_head.close()
    # Create first half of content.opf
    content_head = open('content_head', 'w')
    content_head.write('''<?xml version="1.0"?>
        <package version="2.0" xmlns="http://www.idpf.org/2007/opf"
                 unique-identifier="BookId">
         <metadata xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:opf="http://www.idpf.org/2007/opf">
           <dc:title>''' + 'book_name' + '''</dc:title> 
           <dc:creator>''' + author(toc) + '''</dc:creator>
           <dc:language>ja-JP</dc:language> 
           <dc:rights>Public Domain</dc:rights> 
           <dc:publisher>Nicolas</dc:publisher> 
           <dc:identifier id="bookid">urn:uuid:''' + rand + '''</dc:identifier>
         </metadata>''')                                # Book name TBD
    content_head.close()

def chapter():		                                      # Change argument to extracted chapter url list
    url = 'https://ncode.syosetu.com/n8611bv/1'         # Change to input
    r = requests.get(url)
    r.raise_for_status()
    page = bs4.BeautifulSoup(r.content, "html.parser")
    return page                                         # TBD - returns entire page at the moment


# Get author name
# Get series name
# TODO: Get volume names // If function for situation with no names
# TODO: For volume in volume names
    # Create mimetype, META-INF folder and OEBPS folder
    # Create head for content.opf and toc.ncx
    # TODO: Create bodies and spine for content.opf and toc.ncx
    # TODO: Get chapter urls in dict file
    # TODO: For url in chapter urls
        # TODO: Get chapter name
        # TODO: Append appropriate line to bodies and spine (content, toc)
        # TODO: Get xhtml content for every chapter
        # TODO: Create XML file
    # TODO: Complete toc.ncx and content.opf and join files
    # TODO: Create zip file
    # TODO: Add files to zip file
    # TODO: Change extension to epub

input()
