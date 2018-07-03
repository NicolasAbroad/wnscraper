# chapters.py - Creates chapters (.xhtml) within the epub file
import re

def create_chapter(chapter_title, chapter_string, xhtml_name, epub_file):
    chapter_head = '''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8" />
<link rel="stylesheet" type="text/css" href="vertical.css" class="vertical" title="vertical" />
<link rel="alternate stylesheet" type="text/css" href="horizontal.css" class="horizontal" title="horizontal" />
<title>''' + chapter_title + '''</title>
</head>
<body>''' + '\n<h1>' + chapter_title + '</h1>\n<p> '
    chapter_complete = chapter_head + chapter_string + '</p>\n</body>\n</html>'
    epub_file.writestr('OEBPS/' + xhtml_name + '.xhtml', chapter_complete)

def format_chapter_url(url_regex, tuple_ch_url, input_url):
    unformatted = re.compile(url_regex).findall(tuple_ch_url)
    formatted = unformatted[0]
    chapter_url = input_url + formatted
    return chapter_url
