# essential_files.py - Creates mimetype and content.xml within the epub file

def create_essentials(epub_file):
    epub_file.writestr('mimetype', 'application/epub+zip')

    epub_file.writestr('META-INF/container.xml', '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>''')
