# stylesheet.py - Creates horizontal.css and vertical.css within the epub file


def create_stylesheets(epub_file):
    horizontal = '''html{
    font-family: 'foobar', "HiraMinProN-W3", "@ＭＳ明朝", serif, sans-serif;
    font-size: 14pt;
    margin: auto 1em;
    padding: 1em 0;
    max-width: 28em;}
body{
    margin: 0;
}
h1{
    font-weight: normal;
    line-height: 2;
    font-size: 2em;
    margin-top: 2em;
}'''
    epub_file.writestr('OEBPS/horizontal.css', horizontal)

    vertical = '''html{
    -epub-writing-mode: vertical-rl;
    font-family: 'foobar', "HiraMinProN-W3", "@ＭＳ 明朝", serif, sans-serif;
    font-size: 14pt;
    margin: auto 1em;
    padding: 1em 0;
    max-height: 28em;
}
body{
    margin: 0;
}
h1{
    font-weight: normal;
    line-height: 2;
    font-size: 2em;
    margin-top: 2em;
}'''
    epub_file.writestr('OEBPS/vertical.css', vertical)
