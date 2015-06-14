"""
Script that parses a calibre server log file.

Usage: calibre-access [LOGFILE|-] [-s]

    -s, --searches    Parse search records instead of download records

Licensed under the MIT license (see LICENSE)
"""

__author__ = 'laharah'

import pygeoip
import re
import urllib2
import gzip
import os
import platform
import time
import sys

from collections import namedtuple

import docopt
import appdirs

APPNAME = 'calibre-access'
USER_DIR = appdirs.user_data_dir(APPNAME)
DownloadRecord = namedtuple("DownloadRecord", ['ip', 'date', 'location', 'file'])
SearchRecord = namedtuple("SearchRecord", ['ip', 'date', 'location', 'search'])


def calibre_downloads(log_file=None):
    """
    Generator to yield parsed and geo-located records from the calibre
    server_access_log

    :param log_file: The calibre server_access_log to use. Attempts to locate the log
    if none supplied
    :return: a generator of DownloadRecords
    """
    return _get_records_generator(DownloadRecord, log_file=log_file)


def calibre_searches(log_file=None):
    """
    Generator to yield parsed and geo-located search requests from the calibre
    server_access_log

    :param log_file: The calibre server_access_log to use. Attempts to locate log if
    none supplied
    :return: a generator of SearchRecords
    """
    return _get_records_generator(SearchRecord, log_file=log_file)


def _get_records_generator(StorageTuple, log_file):
    # TODO: smarter expression/storage handling: refactor and simplify
    geo_database = get_database()

    if not log_file:
        log_file = locate_logs()
    if StorageTuple is DownloadRecord:
        records = get_download_strings(log_file)
    else:
        records = get_search_strings(log_file)

    if StorageTuple is DownloadRecord:
        parser = parse_download_string
    else:
        parser = parse_search_string

    for record in records:
        parsed = parser(record, geo_database)
        if parsed:
            yield parsed


def get_download_strings(filename):
    return _get_log_strings(filename, r'.*(\.mobi|\.epub|\.azw|\.azw3).*')


def get_search_strings(filename):
    return _get_log_strings(filename, r'.*POST .*search\?query=.*')


def _get_log_strings(filename, expression):
    if not isinstance(filename, basestring):
        fin = sys.stdin
    else:
        fin = open(filename)

    compiled_expression = re.compile(expression)
    for line in fin:
        match = compiled_expression.match(line)
        if match:
            yield match.group()

    fin.close()


def parse_search_string(record, ipdatabse):
    """
    parses a given search string into a SearchRecord. Prunes repeat searches by
    returning none if search is not unique (by day).
    :param record: single search line from calibre access log
    :param ipdatabse: the ipdatabase to be used for geo-location
    :return: SearchRecord or None
    """
    # Variable accuracy?
    compiled_expression = re.compile(
        r'^(\d+\.\d+\.\d+\.\d+).*\[(.+/.+/\d{4}):.+\].*POST .*/search\?query=(.+)" "')
    match = compiled_expression.search(record)
    if match:
        translated = translate_match(match, ipdatabse, type='search')
        try:
            if translated in parse_search_string.unique_searches:
                return None
        except AttributeError:
            parse_search_string.unique_searches = set(translated)
        else:
            parse_search_string.unique_searches.add(translated)
        return translated


def parse_download_string(record, ipdatabase):
    compiled_expression = re.compile(
        r'^(\d+\.\d+\.\d+\.\d+).*\[(.*)\].*GET /get/\w+/(.+?\.\w{3,5}) ')
    match = compiled_expression.search(record)
    if match:
        return translate_match(match, ipdatabase)


def translate_match(match, ipdatabase, type='download'):
    loc = ipdatabase.record_by_addr(match.group(1))
    if not loc:
        loc = {'city': "NONE", 'region_code': "NONE"}
    try:
        loc_string = ', '.join([loc['city'], loc['region_code']])
    except TypeError:
        loc_string = loc['country_name']

    if type == 'download':
        record = DownloadRecord(match.group(1), match.group(2), loc_string,
                                match.group(3))
    elif type == 'search':
        record = SearchRecord(match.group(1), match.group(2), loc_string, match.group(3))
    else:
        raise ValueError('Unknown record type: \'{}\''.format(type))

    return record


def download_database():
    print("database missing or out of date, attempting to download from " "maxmind...")

    url = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"

    if not os.path.exists(USER_DIR):
        os.makedirs(USER_DIR)

    file_name = os.path.join(USER_DIR, url.split('/')[-1])
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,

    f.close()
    print "\nuncompressing..."
    with open(file_name[:-3], 'wb') as uncompressed:
        with gzip.open(file_name, 'rb') as compressed:
            uncompressed.write(compressed.read())
    print "cleaning up..."
    os.remove(file_name)
    print "Done!"
    return file_name[:-3]


def locate_logs():
    system = platform.system()

    if system == 'Darwin':
        path = os.path.expanduser('~/Library/Preferences/calibre/server_access_log.txt')

    elif system == 'Windows':
        appdata = os.getenv('APPDATA')
        path = os.path.join(appdata, 'calibre', 'server_access_log.txt')

    else:
        path = os.path.expanduser('~/.config/calibre/server_access_log.txt')

    if os.path.exists(path):
        return path
    else:
        if os.path.exists('server_access_log.txt'):
            return 'server_access_log.txt'
        else:
            raise IOError('Could not locate calibre log File.')


def get_database():
    database_path = os.path.join(USER_DIR, 'GeoLiteCity.dat')
    if not os.path.exists(database_path):
        try:
            database_path = download_database()
        except urllib2.URLError:
            print "Could not download new database... Exiting"
            sys.exit(1)

    if time.time() - os.path.getmtime(database_path) > 2628000:
        try:
            database_path = download_database()
        except urllib2.URLError:
            # TODO: change to warning
            print "Could not download new database... Using out of date geoip databse!"

    ipdatabase = pygeoip.GeoIP(database_path)

    return ipdatabase


def main():
    arguments = docopt.docopt(__doc__)
    log_file = arguments["LOGFILE"]
    if not log_file:
        try:
            log_file = locate_logs()
        except IOError as e:
            print e.message
            sys.exit(1)
    elif log_file == '-':
        log_file = sys.stdin
    else:
        if not os.path.exists(log_file):
            print "Given Log file does not exist!"
            sys.exit(1)

    if arguments['--searches']:
        records = calibre_searches
    else:
        records = calibre_downloads

    total_records = 0
    ips = set()

    for record in records(log_file):
        print record
        ips.add(record.ip)
        total_records += 1

    print "Total Records: {}".format(total_records)
    print "Unique Ips: {}".format(len(ips))


if __name__ == '__main__':
    main()
