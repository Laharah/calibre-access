__author__ = 'laharah'

import pygeoip
import re

from collections import namedtuple

DownloadRecord = namedtuple("DownloadRecord",
                            ['ip', 'date', 'location', 'book'])


def load_record_strings():
    with open("server_access_log.txt") as f:
        data = f.readlines()
    for line in data:
        match = re.search(r'.*(\.mobi|\.epub|\.azw).*', line)
        if match:
            yield match.group()
    del data


def parse_record(record):
    pattern = r'^(\d+\.\d+\.\d+\.\d+).*\[(.*)\].*GET /get/\w+/(.+?\.\w{3,5}) '
    match = re.search(pattern, record)
    if match:
        return translate_match(match)


def translate_match(match):
    gi = pygeoip.GeoIP('GeoLiteCity.dat')
    loc = gi.record_by_addr(match.group(1))
    if not loc:
        loc = {'city': "NONE", 'region_code': "NONE"}
    try:
        loc_string = ', '.join([loc['city'], loc['region_code']])
    except TypeError:
        loc_string = loc['country_name']

    download = DownloadRecord(match.group(1), match.group(2), loc_string,
                              match.group(3))
    return download


def main():
    records = load_record_strings()
    download_records = []
    for record in records:
        download_record = parse_record(record)
        print download_record
        download_records.append(download_record)

    print "total downloads: {}".format(len(download_records))
    print "unique ips: {}".format(len({r.ip for r in download_records}))

if __name__ == '__main__':
    main()
