#!/bin/env python

# #######################################################################################################
# Parsing URLs to gather PostgreSQL info from "awesome" lists
# #######################################################################################################
#
# Copyright: Vinícius Abrahão Bazana Schmidt (2018)
# License: PostgreSQL license
# https://github.com/vinnix/awesome-pg/blob/master/legal/LICENSE

# TODO:
#       a) modules and classes
#       b) better logic and error handling, passing references
#       c) multi-thread
#       d) unique names
#       e) get pdf titles

import re
import urllib.request
import markdown
from urlextract import URLExtract
from html.parser import HTMLParser
from urllib.error import URLError, HTTPError
import traceback
import logging
from operator import itemgetter
import itertools
from pprint import pprint
import asyncio
import aiohttp


# #######################################################################################################
# Parser implementation (inhirent HTMLParser) for title tag
# #######################################################################################################
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

# #######################################################################################################
# Used to obtain title
# #######################################################################################################
#async def get_title(url):
def get_title(url):
    request_timeout = 10
    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )

#        async with urllib.request.urlopen(req, timeout=request_timeout) as stream:
        with urllib.request.urlopen(req, timeout=request_timeout) as stream:
            data = stream.read()
        parser = Parser()
        parser.feed(data.decode('utf-8', errors='ignore'))
        title_str = parser.title
        re.sub(r"[\s\t\n\r\']*", ' ', title_str)
        return title_str.strip().replace(r'\n', "") 

    # XXX: Concat error code to returning message
    except HTTPError as e:
        if e.code == 404 or e.code == 403 or e.code == 500 or e.code == 503 or e.code == 501:
            return 0
        else:
            error_message = e.code
            print("EXCEPTION: HTTPError: ", error_message, "URL: ", url)
            return " HTTPError " + str(e.code) + " " + url
    except URLError as e:
        if 'unknown url type' in str(e.reason):
            return 0
        elif 'Name or service not known' in str(e.reason):
            return 0
        elif 'Connection refused' in str(e.reason):
            return 0
        elif 'certificate verify failed: certificate has expired' in str(e.reason):
            return 0
        else:
            error_message = e.reason
            print("EXCEPTION: URLError: ", error_message, "URL: ", url)
            return " URLError " + str(e.reason) + " " + url
    except ValueError:
        print("EXCEPTION: Invalid URL : ", url)
        return " ValueError " + url
    except Exception:
        print("EXCEPTION: URL:", url)
        logging.error(traceback.format_exc())
        return " GeneralException " + url


# #######################################################################################################
# URL simple parser
# #######################################################################################################
def url_parse(address):
    req = urllib.request.Request(address)
    with urllib.request.urlopen(req) as response:
        the_page = response.read().decode('utf-8')
    return the_page


# #######################################################################################################
# Read Template
# #######################################################################################################
def read_template(lines_array = []):
    lines_array = []
    url_list_started = False
    lines_to_parse = []

    try:
        with open("../Awesome.md", "rt") as readme_file:
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

    except FileNotFoundError:
        print("vinnix's Awesome.md file not found!")

    return lines_to_parse


# #######################################################################################################
# Extract Title
# #######################################################################################################
def extract_title(lines_to_parse_ff):

    parsing_list = []
    get_url_re   = r"RAW\((?P<url>https?://[^\s]+)\)"
    for urlnum, to_parse in enumerate(lines_to_parse_ff):
        # XXX: I will come back to this regex later
        # https://docs.python.org/3.6/library/re.html
        url_to_parse = re.search(get_url_re, to_parse)
        # print(to_parse, urlnum)
        # print(url_to_parse.group("url"))
        # print("\n\n")
        parsing_list.append(url_to_parse.group("url"))
        # I do still have more to learn regarding regex in python

    md = markdown.Markdown()
    extractor = URLExtract()
    comp_url_list = []
    item_total = 0

    for pos, url_list in enumerate(parsing_list):
        print(">>>> ", url_list)
        url_text = url_parse(url_list)
        html = md.reset().convert(url_parse(url_list))
        # print(html)# print(html)
        comp_url_list.extend(extractor.gen_urls(html))

    # XXX: Make URL list below as unique
    # Converting using  comp_url_list = set(comp_url_list)
    comp_url_list.sort()
    comp_url_list = [a[0] for a in itertools.groupby(comp_url_list)]

    # denied-listed "URLs"
    # XXX: Generate this list from a file
    # remove will raise error if item is not there, so I should use
    # discard, instead
    #  comp_url_list.discard('foo')
    comp_url_list.remove('Postgres.app')
    comp_url_list.remove('CONTRIBUTING.md')
    comp_url_list.remove('pgconfig.org')
    comp_url_list.remove('PostgreSQL.org')
    comp_url_list.remove('opm.io')

    item_counter = 0
    final_list = []
    for urli in comp_url_list:
        item_counter += 1
        title = get_title(urli)  ## Connect to the site and get the URL
        if title == 0:
            continue
        if title == "":
            title = urli

        tup = dict(url=urli, title=title)
        final_list.append(tup)
        print(f'{item_counter:5} URL:   {urli:30}')
        print(f'{item_counter:5} Title: {title:50}')
        item_total += item_counter

    print("Total URLs counter: ", item_total)
    print("#############################################################################")
    print("#############################################################################")

    pprint(final_list)
    final_list.sort(key=itemgetter("title"))
    pprint(final_list)

    agg_data = []
    for item_title, dataitem in itertools.groupby(final_list, itemgetter('title') ):
        agg_data.append(list(dataitem))

    return agg_data


# #######################################################################################################
# Write to file
# #######################################################################################################
def write_to_file(agg_data):
    with open('../Compiled.md', 'w', encoding="utf-8") as the_file:
        the_file.write("## Compiled list\n\n")
        the_file.write('[<img src="http://vinnix.github.io/vinnix/all/images/PostgreSQL_logo.3colors.svg" align="right" width="100">](https://www.postgresql.org/)\n')

        for ind, item in enumerate(agg_data):
            print("Item:", ind, "Tile:", item[0]['title'], "URL:", item[0]['url'])
            the_file.write("<!-- pos(" + str(ind) + ")  url("+ item[0]['url'] + ") --> \n")
            the_file.write(" * [" + item[0]['title'] + "](" + item[0]['url'] + ") \n")
        the_file.close()


# #######################################################################################################
# Main
# #######################################################################################################

def main():

    lines_to_parse_ff = []
    lines_to_parse_ff = read_template()

    agg_data_ff = []
    agg_data_ff = extract_title(lines_to_parse_ff)

    write_to_file(agg_data_ff)



# #######################################################################################################
#  MAIN Caller
# #######################################################################################################

if __name__ == "__main__":
    main()