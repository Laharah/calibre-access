"""
Script that parses a calibre server log file.

Usage: calibre-access [LOGFILE|-]

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


def calibre_downloads(log_file=None):
    """
    Generator to yield parsed and geo-located records from the calibre
    server_access_log

    :param log_file: The calibre server_access_log to use. Attempts to locate one if
    not supplied. Also accepts '-' for stdin.
    :return: a generator of DownloadRecords
    """
    if not log_file:
        log_file = locate_logs()
    records = get_download_strings(log_file)
    geo_database = get_database()
    for record in records:
        yield parse_download_string(record, geo_database)


def get_download_strings(filename):
    if filename == '-':
        fin = sys.stdin
    else:
        fin = open(filename, 'rU')

    compiled_expression = re.compile(r'.*(\.mobi|\.epub|\.azw).*')
    for line in fin:
        match = compiled_expression.match(line)
        if match:
            yield match.group()

    fin.close()


def parse_download_string(record, ipdatabase):
    compiled_expression = re.compile(
        r'^(\d+\.\d+\.\d+\.\d+).*\[(.*)\].*GET /get/\w+/(.+?\.\w{3,5}) ')
    match = compiled_expression.search(record)
    if match:
        return translate_match(match, ipdatabase)


def translate_match(match, ipdatabase):
    loc = ipdatabase.record_by_addr(match.group(1))
    if not loc:
        loc = {'city': "NONE", 'region_code': "NONE"}
    try:
        loc_string = ', '.join([loc['city'], loc['region_code']])
    except TypeError:
        loc_string = loc['country_name']

    download = DownloadRecord(match.group(1), match.group(2), loc_string, match.group(3))
    return download


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
        pass
    else:
        if not os.path.exists(log_file):
            print "Given Log file does not exist!"
            sys.exit(1)

    total_records = 0
    ips = set()
    for record in calibre_downloads(log_file):
        print record
        ips.add(record.ip)
        total_records += 1

    print "Total Downloads: {}".format(total_records)
    print "Unique Ips: {}".format(len(ips))


if __name__ == '__main__':
    main()
