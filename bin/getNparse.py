#!/bin/env python

#
# Parsing URLs to gather PostgreSQL info from "awesome" lists
#

import re
import urllib.request
import markdown
from urlextract import URLExtract
from html.parser import HTMLParser
from urllib.error import URLError, HTTPError
import traceback
import logging


# ################################################################
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ''
        self._in_title_tag = False

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self._in_title_tag = True

    def handle_data(self, data):
        if self._in_title_tag:
            self.title += data

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title_tag = False

# ################################################################


def get_title(url):
    print("Getting title from: ", url)
    request_timeout = 10

    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=request_timeout) as stream:
            data = stream.read()
        parser = Parser()
        parser.feed(data.decode('utf-8', errors='ignore'))
        return parser.title

    except HTTPError as e:
        error_message = e.code
        print("EXCEPTION: HTTPError: ", error_message, "URL: ", url)
        return
    except URLError as e:
        error_message = e.reason
        print("EXCEPTION: URLError: ", error_message, "URL: ", url)
        return
    except ValueError:
        print("EXCEPTION: Invalid URL : ", url)
        return
    except Exception:
        print("EXCEPTION: URL:", url)
        logging.error(traceback.format_exc())


def url_parse(address):
    req = urllib.request.Request(address)
    with urllib.request.urlopen(req) as response:
        the_page = response.read().decode('utf-8')
    return the_page


# ################################################################


lines_array = []
lines_to_parse = []
url_list_started = False
parsing_list = []
try:
    with open("../README.md", "rt") as readme_file:
        for line in readme_file:
            lines_array.append(line.rstrip('\n'))

    url_start_exp = re.compile(r"BEGIN.*URL_LIST_TO_PARSE", re.IGNORECASE)
    url_end_exp = re.compile(r"END.*URL_LIST_TO_PARSE", re.IGNORECASE)

    for linenum, element in enumerate(lines_array):
        # Only check if the list mark/comment that points to the end of the URL list
        # if we are already in appending mode. Otherwise there is no point to very it.
        if url_list_started and url_end_exp.search(element):
            url_list_started = False

        if url_list_started:
            lines_to_parse.append(element)

        # The first boolean verification of the expression below is to avoid unnecessary
        # RE search.
        if url_list_started or url_start_exp.search(element):
            url_list_started = True

        # XXX Another possibility is: once knowing the "linenum" of the BEGIN and the END
        # just do for loop and append the array, but it seems to be extra work.
        # Need to confirm if this makes sense. That's why I tried to avoid unnecessary regular
        # expressions check. Ideally this script should be able
        # to parse large files in a non-expensive way.

    for urlnum, to_parse in enumerate(lines_to_parse):
        # XXX: I will come back to this regex later
        # https://docs.python.org/3.6/library/re.html
        url_to_parse = re.search("RAW\((?P<url>https?://[^\s]+)\)", to_parse)
        # print(to_parse, urlnum)
        # print(url_to_parse.group("url"))
        # print("\n\n")
        parsing_list.append(url_to_parse.group("url"))
        # I do still have more to learn regarding regex in python

    md = markdown.Markdown()
    extractor = URLExtract()

    item_total = 0
    for pos, url_list in enumerate(parsing_list):
        print(">>>> ", url_list)
        url_text = url_parse(url_list)
        html = md.reset().convert(url_parse(url_list))
        item_counter = 0
        for urli in extractor.gen_urls(html):
            # blacklisted "URLs"
            # XXX: Generate this list from a file
            if urli != "Postgres.app" and urli != "CONTRIBUTING.md" \
                    and urli != "pgconfig.org" and urli != 'PostgreSQL.org'\
                    and urli != 'opm.io':
                item_counter += 1
                title = ""
                title = get_title(urli)
                print("Title:", title, "URL: ", urli)
        print("List URLs counter: ", item_counter)
        item_total += item_counter
        #
        # print(html)
    print("Total URLs counter: ", item_total)

except FileNotFoundError:
    print("vinnix's README.md file not found!")
