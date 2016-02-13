"""
Script that parses a calibre server log file.

Usage: calibre-access [options] [LOGFILE|-]

    -d, --downloads   Parse download records (defaut record if none specified)
    -s, --searches    Parse search records
    -b, --bare        do not show total records or total unique ip's
    --time-filter s   number of seconds to filter out non-unique records by.
                      this filters rapid reloads/downloads. defaults to 10



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
import utilities

APPNAME = 'calibre-access'
USER_DIR = appdirs.user_data_dir(APPNAME)


def print_record(record):
    """ prints a download/search record to the terminal in a standardized way"""
    #type, ip, os, date, loc, data
    line = """{r[host]:15}\t{:12}\t{}\t{r[location]:25}\t{r[type]:9}: {r[info]}"""

    os = record['os']
    if 'Android' in os:
        os = 'Android'
    else:
        try:
            os = os.split()[0].strip(';')
        except IndexError:
            os = os

    date = record['datetime'].strftime('%d/%b/%Y:%H:%M:%S')

    print line.format(os, date, r=record)


def calibre_downloads(log_file=None):
    """
    convienience method: creates a generator of all calibre download records

    :param log_file: The calibre server_access_log to use. Attempts to locate the log
    if none supplied
    :return: a generator of parsed log lines regarding file downloads
    """
    if not log_file:
        log_file = locate_logs()
    lines = get_lines_from_file(log_file)
    return utilities.get_records(lines, [download_coro])


def calibre_searches(log_file=None):
    """
    convienience method: creates a generator of all calibre search records

    :param log_file: The calibre server_access_log to use. Attempts to locate the log
    if none supplied
    :return: a generator of parsed log lines regarding search requests
    """
    if not log_file:
        log_file = locate_logs()
    lines = get_lines_from_file(log_file)
    return utilities.get_records(lines, [search_coro])

def all_records(log_file=None):
    """
    convienience function to create a generator of all parsed calibre-webserver Records.
    """
    if not log_file:
        log_file = locate_logs()
    lines = get_lines_from_file(log_file)
    return utilities.parse_generic_server_log_line(lines)


def download_coro():
    """ coroutine to filter and parse download records"""
    pattern = re.compile(r'.*(\.mobi|\.epub|\.azw|\.azw3|\.pdf)')
    record = None
    while True:
        line = yield record
        if not pattern.match(line):
            record = None
            continue
        record = next(utilities.parse_generic_server_log_line([line]))
        record['type'] = 'download'
        record['file'] = record['request'].split('/')[-1]
        record['info'] = record['file']


def search_coro():
    """coroutine to filter and parse search records"""
    pattern = re.compile(r'\] "GET /browse/search\?query=(\S*)')
    record = None
    while True:
        line = yield record
        match = pattern.search(line)
        if not match:
            record = None
            continue
        record = next(utilities.parse_generic_server_log_line([line]))
        record['type'] = 'search'
        record['query'] = match.group(1)
        record['info'] = match.group(1)


def get_lines_from_file(filepath):
    with open(filepath, 'rU') as f:
        for line in f:
            yield line


#########
#  Section: db_management
#########

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
    """returns the pygeoip database, downloads if out of date or missing"""
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

    coros = []
    if arguments['--searches']:
        coros.append(search_coro)
    if arguments['--downloads']:
        coros.append(download_coro)
    if not coros:
        coros = [download_coro]


    if log_file is not sys.stdin:
        log_file = get_lines_from_file(log_file)

    ipdatabase = get_database()
    time_filter = arguments['--time-filter']
    time_filter = 10 if time_filter is None else int(time_filter)

    records = utilities.get_records(log_file, coros)
    records = utilities.time_filter(records, time_filter)
    records = utilities.get_locations(records, ipdatabase)
    records = utilities.get_os_from_agents(records)

    total_records = 0
    ips = set()

    for record in records:
        print_record(record)
        ips.add(record['host'])
        total_records += 1

    if not arguments['--bare']:
        print "Total Records: {}".format(total_records)
        print "Unique Ips: {}".format(len(ips))




if __name__ == '__main__':
    main()
