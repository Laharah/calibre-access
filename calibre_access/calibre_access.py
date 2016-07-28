from __future__ import unicode_literals, print_function, division
__doc__ = """
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
import gzip
import os
import platform
import glob
import time
import sys
import warnings

import appdirs
import requests
from . import utilities

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

    print(line.format(os, date, r=record))


def calibre_downloads(log_files=None):
    """
    convienience method: creates a generator of all calibre download records

    :param log_files: The calibre server_access_log to use. Attempts to locate the log
    if none supplied
    :return: a generator of parsed log lines regarding file downloads
    """
    if not log_files:
        log_files = locate_logs()
    lines = utilities.get_lines_from_logs(log_files)
    return utilities.get_records(lines, [download_coro])


def calibre_searches(log_files=None):
    """
    convienience method: creates a generator of all calibre search records

    :param log_files: The calibre server_access_log to use. Attempts to locate the log
    if none supplied
    :return: a generator of parsed log lines regarding search requests
    """
    if not log_files:
        log_files = locate_logs()
    lines = utilities.get_lines_from_logs(log_files)
    return utilities.get_records(lines, [search_coro])


def all_records(log_files=None):
    """
    convienience function to create a generator of all parsed calibre-webserver Records.
    """
    if not log_files:
        log_files = locate_logs()
    lines = utilities.get_lines_from_logs(log_files)
    return utilities.parse_generic_server_log_line(lines)


def download_coro():
    """ coroutine to filter and parse download records"""
    pattern = re.compile(r'.*(\.mobi|\.epub|\.azw|\.azw3|\.pdf)')
    record = None
    record_coro = utilities.coro_from_gen(utilities.parse_generic_server_log_line)
    next(record_coro)
    while True:
        line = yield record
        if not pattern.match(line):
            record = None
            continue
        record = record_coro.send(line)
        record['type'] = 'download'
        record['file'] = record['request'].split('/')[-1]
        record['info'] = record['file']


def search_coro():
    """coroutine to filter and parse search records"""
    pattern = re.compile(r'\] "GET /browse/search\?query=(\S*)')
    record = None
    record_coro = utilities.coro_from_gen(utilities.parse_generic_server_log_line)
    next(record_coro)
    while True:
        line = yield record
        match = pattern.search(line)
        if not match:
            record = None
            continue
        record = record_coro.send(line)
        record['type'] = 'search'
        record['query'] = match.group(1)
        record['info'] = match.group(1)

#########
#  Section: db_management
#########


def download_database():
    print("database missing or out of date, attempting to download from "
          "maxmind...",
          file=sys.stderr)

    url = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"

    if not os.path.exists(USER_DIR):
        os.makedirs(USER_DIR)

    file_name = os.path.join(USER_DIR, url.split('/')[-1])
    r = requests.get(url, stream=True)
    file_size = int(r.headers['Content-Length'])
    print("Downloading: %s Bytes: %s" % (file_name, file_size), file=sys.stderr)

    downloaded = 0
    chunksize = 8192
    print('\n', end='')
    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunksize):
            downloaded += len(chunk)
            status = '[{: <50}] {:02}% done'
            status = status.format('#' * (1 + int(downloaded // (file_size / 50))),
                                   int((downloaded / file_size) * 100))
            print(status, end='\r', file=sys.stderr)
            f.write(chunk)

    print("\nuncompressing...", file=sys.stderr)
    with open(file_name[:-3], 'wb') as uncompressed:
        with gzip.open(file_name, 'rb') as compressed:
            uncompressed.write(compressed.read())
    print("cleaning up...", file=sys.stderr)
    os.remove(file_name)
    print("Done!", file=sys.stderr)
    return file_name[:-3]


def get_search_dir():
    system = platform.system()
    if system == 'Darwin':
        path = os.path.expanduser('~/Library/Preferences/calibre')

    elif system == 'Windows':
        appdata = os.getenv('APPDATA')
        path = os.path.join(appdata, 'calibre')

    else:
        path = os.path.expanduser('~/.config/calibre')
    return path


def locate_logs():
    path = get_search_dir()

    if os.path.exists(path):
        return glob.glob(os.path.join(path, 'server_access_log.txt*'))

    local = glob.glob('server_access_log.txt*')
    if not local:
        raise IOError('Could not locate calibre log File.')
    else:
        return local


def get_database():
    """returns the pygeoip database, downloads if out of date or missing"""
    database_path = os.path.join(USER_DIR, 'GeoLiteCity.dat')
    if not os.path.exists(database_path):
        try:
            database_path = download_database()
        except requests.ConnectionError:
            raise

    if time.time() - os.path.getmtime(database_path) > 2628000:
        try:
            database_path = download_database()
        except requests.ConnectionError:
            warnings.warn("Could not download new database... "
                          "Using out of date geoip databse!")

    ipdatabase = pygeoip.GeoIP(database_path)

    return ipdatabase


def main():
    import docopt

    arguments = docopt.docopt(__doc__)
    log_file = arguments["LOGFILE"]
    if not log_file:
        try:
            log_file = locate_logs()
        except IOError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
    elif log_file == '-':
        log_file = sys.stdin
    else:
        if not os.path.exists(log_file):
            print("Given Log file does not exist!", file=sys.stderr)
            sys.exit(1)

    coros = []
    if arguments['--searches']:
        coros.append(search_coro)
    if arguments['--downloads']:
        coros.append(download_coro)
    if not coros:
        coros = [download_coro]

    if log_file is not sys.stdin:
        log_file = utilities.get_lines_from_logs(log_file)

    try:
        ipdatabase = get_database()
    except requests.ConnectionError as e:
        print("Could not connect to Maxmind to download new database, Exiting!",
              file=sys.stderr)
        sys.exit(1)
    time_filter_len = arguments['--time-filter']
    time_filter_len = 10 if time_filter_len is None else int(time_filter_len)

    base_records = utilities.get_records(log_file, coros)
    time_filtered = utilities.time_filter(base_records, time_filter_len)
    geo_located = utilities.get_locations(time_filtered, ipdatabase)
    records = utilities.get_os_from_agents(geo_located)

    total_records = 0
    ips = set()

    for record in records:
        print_record(record)
        ips.add(record['host'])
        total_records += 1

    if not arguments['--bare']:
        print("Total Records: {}".format(total_records))
        print("Unique Ips: {}".format(len(ips)))

    sys.exit(0)
