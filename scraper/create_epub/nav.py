# nav.py - Creates nav.xhtml within the epub file


def create_nav(epub_file):
    nav = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US" lang="en-US">
    <head>
        <title>EPUB 3 Navigation Document</title>
        <meta charset="utf-8"/>
        <link rel="vertical" type="text/css" href="css/vertical.css"/>
        <link rel="horizontal" type="text/css" href="horizontal.css"/>
    </head>
    <body>
        <nav epub:type="toc" id="toc"><ol></ol></nav>
    </body>
</html>'''
    epub_file.writestr('OEBPS/nav.xhtml', nav)
