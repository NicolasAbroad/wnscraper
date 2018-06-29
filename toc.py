# toc.py - Creates toc.ncx within the epub file

def create_toc(uid, volume_title):          # Creates start of toc.ncx string
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

def add_nav(toc_string, xhtml_name, order):      # Adds one nav point to toc.ncx string
    toc_string += '\n' + '''<navPoint id="''' + xhtml_name + '''" playOrder ="''' + str(order) + '''">
            <navLabel>
                <text>"''' + xhtml_name + '''"</text>
            </navLabel>
        <content src="''' + xhtml_name + '''.xhtml"/>
        </navPoint>'''
    return toc_string

def finish_toc(toc_string, epub_file):                     # Adds final lines to toc.ncx string and creates file
    toc_string += '\n</navMap>\n</ncx>'
    epub_file .writestr('OEBPS/toc.ncx', toc_string)
