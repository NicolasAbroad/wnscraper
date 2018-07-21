# mimetype.py - Creates mimetype within the epub file


def create_mimetype(epub_file):
    epub_file.writestr('mimetype', 'application/epub+zip')
