# content.py - Creates content.opf within the epub file

def create_content(volume_title, author_name, uid):         # Creates start of content.opf string
    content_string = '''<?xml version="1.0" encoding="UTF-8"?>
<package prefix="cc: http://creativecommons.org/ns#" unique-identifier="uid" version="3.0" xml:lang="en" xmlns="http://www.idpf.org/2007/opf">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
		<meta property="dcterms:modified">2010-02-17T04:39:13Z</meta>
        <dc:title>''' + volume_title + '''</dc:title>
        <dc:creator id="creator">''' + author_name + '''</dc:creator>
        <dc:language>ja-JP</dc:language>
        <dc:rights>Public Domain</dc:rights>
        <dc:publisher>Nicolas</dc:publisher>
        <dc:identifier id="uid">''' + uid + '''</dc:identifier>
    </metadata>
    <manifest >
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item href="nav.xhtml" id="nav" media-type="application/xhtml+xml" properties="nav"/>
		<item id="vstyle" href="vertical.css" media-type="text/css"/>
        <item id="hstyle" href="horizontal.css" media-type="text/css"/>
        <item id="pagetemplate" href="page-template.xpgt" media-type="application/vnd.adobe-page-template+xml"/>''' + '\n'
    return content_string

def add_item_id(content_string, xhtml_name):              # Adds one item id to content.opf string
    content_string += '        <item id ="' + xhtml_name + '" href="' + xhtml_name + '.xhtml" media-type="application/xhtml+xml"/>\n'
    return content_string

def create_middle():                          # Finishes manifest section and starts spine section in content.opf string
    content_string = '    </manifest>\n    <spine toc="ncx" page-progression-direction="rtl">\n		<itemref idref="nav"/>\n'
    return content_string

def add_itemref(content_string, xhtml_name):                            # Adds one itemref to content.opf string
    content_string += '        <itemref idref ="' + xhtml_name + '"/>\n'
    return content_string

def finish_content(content_string, epub_file):                                 # Adds final lines to content.opf string and creates file
    content_string += '    </spine>\n</package>'
    epub_file.writestr('OEBPS/content.opf', content_string)
