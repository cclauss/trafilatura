# -*- coding: utf-8 -*-
# pylint:disable-msg=E0611,I1101
"""
Module bundling functions related to HTML and text processing.
"""

import logging
import re

from io import StringIO # python3

import cchardet as chardet
import requests
from lxml import etree, html


LOGGER = logging.getLogger(__name__)


CUSTOM_HTMLPARSER = html.HTMLParser()

UNICODE_WHITESPACE = re.compile(u'[\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000]')


def fetch_url(url):
    """ Fetch page using requests """
    response = requests.get(url)
    if int(response.status_code) != 200:
        return None
    LOGGER.debug('response encoding: %s', response.encoding)
    guessed_encoding = chardet.detect(response.content)['encoding']
    LOGGER.debug('guessed encoding: %s', guessed_encoding)
    if guessed_encoding is not None:
        try:
            htmltext = response.content.decode(guessed_encoding)
        except UnicodeDecodeError:
            htmltext = response.text
    else:
        htmltext = response.text
    return htmltext


def load_html(htmlobject):
    """Load object given as input and validate its type (accepted: LXML tree and string)"""
    if isinstance(htmlobject, (etree._ElementTree, html.HtmlElement)):
        # copy tree
        tree = htmlobject
    elif isinstance(htmlobject, str):
        ## robust parsing
        try:
            #guessed_encoding = chardet.detect(htmlobject.encode())['encoding']
            #LOGGER.info('guessed encoding: %s', guessed_encoding)
            # parse
            # parser = html.HTMLParser() # encoding=guessed_encoding  # document_fromstring
            tree = html.parse(StringIO(htmlobject), parser=CUSTOM_HTMLPARSER)
        except UnicodeDecodeError as err:
            LOGGER.error('unicode %s', err)
            tree = None
        except UnboundLocalError as err:
            LOGGER.error('parsed string %s', err)
            tree = None
        except (etree.XMLSyntaxError, ValueError, AttributeError) as err:
            LOGGER.error('parser %s', err)
            tree = None
    else:
        LOGGER.error('this type cannot be processed: %s', type(htmlobject))
        tree = None
    return tree


def sanitize(text):
    '''Convert text and discard incompatible unicode and invalid XML characters'''
    # TODO: remove control characters in sanitizer
    # text = ' '.join(text.split())
    #all unicode characters from 0x0000 - 0x0020 (33 total) are bad and will be replaced by "" (empty string)
    # newtext = ''
    #for line in text:
    #    for pos in range(0,len(line)):
    #        if ord(line[pos]) < 32:
    #            line[pos] = None
    #newtext = newtext + u''.join([c for c in line if c]) + '\n'
    #return newtext
    text = text.replace('\r\n', '\n')
    # invalid_xml = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
    # text = invalid_xml.sub('', text)
    #\x0b\x0c\r\x1c\x1d\x1e\x1f \x85\xa0
    text = UNICODE_WHITESPACE.sub('', text)
    text = re.sub(r'&#13;|', '', text)
    # filter out empty lines
    returntext = ''
    for line in text.splitlines():
        if not re.match(r'[\s\t]*$', line):
            # line = line.replace('\s\s\s', '\s')
            returntext += line + '\n'
    return returntext


def trim(string):
    """Remove spaces at the beginning and end of a string"""
    # string = re.sub(r'\n+', '\n', string, re.MULTILINE)
    string = re.sub(r'\s+', ' ', string.strip(' \t\n\r'), re.MULTILINE)
    string = string.strip()
    return string