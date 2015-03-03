__author__ = 'laharah'

import pygeoip
import re

from collections import namedtuple

DownloadRecord = namedtuple("DownloadRecord",
                            ['ip', 'date', 'location', 'book'])


def load_record_strings():
    with open("server_access_log.txt") as f:
        data = f.readlines()
    records = []
    for line in data:
        match = re.search(r'.*(\.mobi|\.epub).*', line)
        if match:
            records.append(match.group())

    return records


def parse_records(records):
    downloads = []
    pattern = r'^(\d+\.\d+\.\d+\.\d+).*\[(.*)\].*GET /get/\w+/(.+?\.\w{3,5}) '
    for line in records:
        match = re.search(pattern, line)
        if match:
            downloads.append(match)
    return translate_matches(downloads)


def translate_matches(matches):
    downloads = []
    gi = pygeoip.GeoIP('GeoLiteCity.dat')
    for match in matches:
        loc = gi.record_by_addr(match.group(1))
        if not loc:
            downloads.append(match.groups())
            continue
        try:
            loc_string = ', '.join([loc['city'], loc['region_code']])
        except TypeError:
            loc_string = loc['metro_code']
        downloads.append(
            DownloadRecord(match.group(1), match.group(2), loc_string,
                           match.group(3)))
    return downloads


def main():
    records = load_record_strings()
    downloads = parse_records(records)
    for dl in downloads:
        print dl


if __name__ == '__main__':
    main()
