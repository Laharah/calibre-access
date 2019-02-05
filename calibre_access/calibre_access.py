from __future__ import unicode_literals, print_function, division
__doc__ = """
Script that parses a calibre server log file.

Usage: calibre-access [options] [LOGFILE|-]

    -d, --downloads   Parse download records (defaut record if none specified)
    -s, --searches    Parse search records
    -r, --reads       Parse read book records
    -v, --views       Parse view book detail records
    -a, --all         equivalent to -dsrv
    -b, --bare        do not show total records or total unique ip's
    --set-library=PTH use library to resolve book ids, saved between runs
    --time-filter s   number of seconds to filter out non-unique records by.
                      this filters rapid reloads/downloads. defaults to 10,
    --force-refresh   Force a refresh of the GeoLite database



Licensed under the MIT license (see LICENSE)
"""

__author__ = 'laharah'

import json
import re
import tarfile
import os
import platform
import glob
import time
import sys
import warnings
import urllib

import geoip2.database
import appdirs
import requests
from . import utilities

APPNAME = 'calibre-access'
USER_DIR = appdirs.user_data_dir(APPNAME)
USER_CONFIG_DIR = appdirs.user_config_dir(APPNAME)


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
    :return: a generator of parsed log lines regarding file downloads """
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
    """coroutine to filter and parse download records"""
    pattern_old = re.compile(r'.*(\.mobi|\.epub|\.azw|\.azw3|\.pdf)')
    pattern_new = re.compile(r'.* (?:/legacy)?/get/(EPUB|MOBI|PDF|AZW|AZW3)/(\d+)')
    record = None
    record_coro = utilities.coro_from_gen(utilities.parse_generic_server_log_line)
    next(record_coro)
    while True:
        line = yield record
        match = pattern_new.match(line) or pattern_old.match(line)
        if not match:
            record = None
            continue
        record = record_coro.send(line)
        record['type'] = 'download'
        if not record['timezone']:  #old type log line
            record['file'] = record['request'].split('/')[-1]
            record['info'] = record['file']
        else:
            record['file'] = None
            record['book_id'] = match.group(2)
            record['info'] = 'Book ID: {}'.format(record['book_id'])


def search_coro():
    """coroutine to filter and parse search records"""
    pattern_old = re.compile(r'.*\] "GET /browse/search\?query=(\S*)')
    pattern_new = re.compile(r'.*&search=([^&]+?)&')
    if sys.version_info.major == 2:
        unquote = urllib.unquote_plus
    else:
        unquote = urllib.parse.unquote_plus
    record = None
    record_coro = utilities.coro_from_gen(utilities.parse_generic_server_log_line)
    next(record_coro)
    while True:
        line = yield record
        match = pattern_old.match(line) or pattern_new.match(line)
        if not match:
            record = None
            continue
        record = record_coro.send(line)
        record['type'] = 'search'
        record['query'] = unquote(match.group(1))
        record['info'] = record['query']


def read_coro():
    """coroutine to filter and parse reading records"""
    pattern = re.compile(r'.*/book-manifest/(\d+)/(EPUB|MOBI|PDF|AZW|AZW3)')
    record = None
    record_coro = utilities.coro_from_gen(utilities.parse_generic_server_log_line)
    next(record_coro)
    while True:
        line = yield record
        match = pattern.match(line)
        if not match:
            record = None
            continue
        record = record_coro.send(line)
        record['type'] = 'read'
        record['book_id'] = match.group(1)
        record['info'] = 'Book ID: {}'.format(record['book_id'])


def view_coro():
    """coroutine to filter and parse reading records"""
    # 192.168.0.1 port-56702 - 29/Jul/2017:09:26:37 -0700 "GET /get/cover/21469/Calibre_Library HTTP/1.1" 200 459389
    pattern = re.compile(r'.* /get/cover/(\d+)/([^\?])+? ')
    record = None
    record_coro = utilities.coro_from_gen(utilities.parse_generic_server_log_line)
    next(record_coro)
    while True:
        line = yield record
        match = pattern.match(line)
        if not match:
            record = None
            continue
        record = record_coro.send(line)
        record['type'] = 'view'
        record['book_id'] = match.group(1)
        record['info'] = 'Book ID: {}'.format(record['book_id'])


#########
#  Section: db_management
#########


def download_database():
    print(
        "database missing or out of date, attempting to download from "
        "maxmind...",
        file=sys.stderr)

    url = "https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz"

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
    with tarfile.open(file_name, 'r:gz') as f:
        names = f.getnames()
        db_name = glob.fnmatch.filter(names, '*.mmdb')[0]
        f.extract(db_name, path=USER_DIR)
    db_path = os.path.join(USER_DIR, db_name)
    print("cleaning up...", file=sys.stderr)
    os.rename(db_path, os.path.join(USER_DIR, 'GeoLite2-City.mmdb'))
    os.rmdir(os.path.join(USER_DIR, os.path.split(db_name)[0]))
    os.remove(file_name)
    print("Done!", file=sys.stderr)
    return os.path.join(USER_DIR, 'GeoLite2-City.mmdb')


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
        return sorted(
            glob.glob(os.path.join(path, 'server_access_log.txt*')), reverse=True)

    local = glob.glob('server_access_log.txt*')
    if not local:
        raise IOError('Could not locate calibre log File.')
    else:
        return sorted(local, reverse=True)


def get_database(force_refresh=False):
    """returns the pygeoip database, downloads if out of date or missing"""
    database_path = os.path.join(USER_DIR, 'GeoLite2-City.mmdb')
    if not os.path.exists(database_path):
        try:
            database_path = download_database()
        except requests.ConnectionError:
            raise

    if (time.time() - os.path.getmtime(database_path) > 2628000 or force_refresh):
        try:
            database_path = download_database()
        except requests.ConnectionError:
            warnings.warn("Could not download new database... "
                          "Using out of date geoip databse!")

    ipdatabase = geoip2.database.Reader(database_path)

    return ipdatabase


def main():
    import docopt

    arguments = docopt.docopt(__doc__)

    config_file = os.path.join(USER_CONFIG_DIR, 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r') as fin:
            config = json.load(fin)
    else:
        config = {'library_path': None}

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
        log_file = [log_file]

    coros = []
    arg_to_coro = {
        '--downloads': download_coro,
        '--searches':  search_coro,
        '--reads':     read_coro,
        '--views':     view_coro,
    } #yapf:disable

    for arg, coro in arg_to_coro.items():
        if arguments[arg]:
            coros.append(coro)

    if arguments['--all']:
        coros = list(arg_to_coro.values())
    if not coros:
        coros = [download_coro]

    if log_file is not sys.stdin:
        log_file = utilities.get_lines_from_logs(log_file)

    try:
        ipdatabase = get_database(arguments['--force-refresh'])
    except requests.ConnectionError:
        print(
            "Could not connect to Maxmind to download new database, Exiting!",
            file=sys.stderr)
        sys.exit(1)
    time_filter_len = arguments['--time-filter']
    time_filter_len = 10 if time_filter_len is None else int(time_filter_len)

    base_records = utilities.get_records(log_file, coros)
    geo_located = utilities.get_locations(base_records, ipdatabase)
    records = utilities.get_os_from_agents(geo_located)

    if arguments['--set-library'] is None and config['library_path']:
        arguments['--set-library'] = config['library_path']
    if arguments['--set-library'] and os.path.exists(arguments['--set-library']):
        path = os.path.abspath(arguments['--set-library'])
        arguments['--set-library'] = path
        if not path.endswith('metadata.db'):
            path = os.path.join(path, 'metadata.db')
        records = utilities.resolve_book_ids(records, path)

    records = utilities.time_filter(records, time_filter_len)  # time filter must be last

    total_records = 0
    ips = set()

    for record in records:
        print_record(record)
        ips.add(record['host'])
        total_records += 1

    if not arguments['--bare']:
        print("Total Records: {}".format(total_records))
        print("Unique Ips: {}".format(len(ips)))

    if arguments['--set-library']:
        config['library_path'] = arguments['--set-library']
        if not os.path.exists(USER_CONFIG_DIR):
            os.makedirs(USER_CONFIG_DIR)
        with open(config_file, 'w') as fout:
            json.dump(config, fout)

    sys.exit(0)
