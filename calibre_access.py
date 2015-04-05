"""
Script that parses a calibre server log file.

Usage: calibre-access [LOGFILE]

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

from collections import namedtuple

import docopt
import appdirs

APPNAME = 'calibre-access'
USER_DIR = appdirs.user_data_dir(APPNAME)
DownloadRecord = namedtuple("DownloadRecord",
                            ['ip', 'date', 'location', 'book'])


def load_record_strings(filename):
    with open(filename) as f:
        data = f.readlines()
    for line in data:
        match = re.search(r'.*(\.mobi|\.epub|\.azw).*', line)
        if match:
            yield match.group()
    del data


def parse_record(record, ipdatabase):
    pattern = r'^(\d+\.\d+\.\d+\.\d+).*\[(.*)\].*GET /get/\w+/(.+?\.\w{3,5}) '
    match = re.search(pattern, record)
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

    download = DownloadRecord(match.group(1), match.group(2), loc_string,
                              match.group(3))
    return download


def download_database():
    print ("database missing or out of date, attempting to download from "
           "maxmind...")

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
        status = status + chr(8)*(len(status)+1)
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
        path = os.path.expanduser(
            '~/Library/Preferences/calibre/server_access_log.txt')

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
            print 'ERROR: Could not locate log file.'
            exit(1)

def get_database():
    database_path = os.path.join(USER_DIR, 'GeoLiteCity.dat')
    if not os.path.exists(database_path):
        database_path = download_database()

    if time.time() - os.path.getmtime(database_path) > 2628000:
        os.remove(database_path)
        database_path = download_database()

    ipdatabase = pygeoip.GeoIP(database_path)


    return ipdatabase

def main():
    arguments = docopt.docopt(__doc__)
    log_file = arguments["LOGFILE"]
    if not log_file:
        log_file = locate_logs()
    if not os.path.exists(log_file):
        print "Given Log file does not exsist!"
        exit(1)
    records = load_record_strings(log_file)
    download_records = []
    ipdatabase = get_database()
    for record in records:
        download_record = parse_record(record, ipdatabase)
        print download_record
        download_records.append(download_record)

    print "total downloads: {}".format(len(download_records))
    print "unique ips: {}".format(len({r.ip for r in download_records}))

if __name__ == '__main__':
    main()
