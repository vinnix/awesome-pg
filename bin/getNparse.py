#!/bin/env python


#
# Parsing URLs to gather PostgreSQL info from "awesome" lists
#

import re

lines_array = []
lines_to_parse = []
url_list_started = False
try:
    with open("../README.md","rt") as readme_file:
      for line in readme_file:
         lines_array.append(line.rstrip('\n'))

    url_start_exp = re.compile(r"BEGIN.*URL_LIST_TO_PARSE",re.IGNORECASE)
    url_end_exp = re.compile(r"END.*URL_LIST_TO_PARSE",re.IGNORECASE)

    for linenum,element in enumerate(lines_array):

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

      ## XXX Another possibility is: once knowing the "linenum" of the BEGIN and the END
      ## just do for loop and append the array, but it seems to be extra work.
      ## Need to confirm if this makes sense. That's why I tried to avoid unnecessary regular
      ## expressions check. Ideally this script should be able to parse large files in a non-expensive way.


    for urlnum,to_parse in enumerate(lines_to_parse):
      print(to_parse,urlnum)

except FileNotFoundError:
    print("vinnix's README file not found!")


