# check_url.py - checks if url matches one of the compatible sources
# compatible sources: ncode.syosetu.com


import re


def input_url_source_check(input_url):
    sources_regex = {'syosetu': '((http:\/\/|https:\/\/)?(ncode.syosetu.com\/n))(\d{4}[a-z]{2}\/?)$'}
    for key in sources_regex:
        regex = re.compile(sources_regex[key])
        if re.match(regex, input_url):
            return key
        else:
            return False