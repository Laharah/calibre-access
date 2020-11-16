from __future__ import unicode_literals, absolute_import

import calibre_access.utilities as utilities
import re
import datetime
import mock
import geoip2.models
from geoip2.errors import AddressNotFoundError
import copy
from .fixtures import mock_access_logs_local, mock_db_file


def test_get_lines_from_logs(mock_access_logs_local):
    lines = ['fake access data\n'] * 8
    assert list(utilities.get_lines_from_logs(mock_access_logs_local)) == lines


def test_get_records():
    lines = "paaaaattern pattern no_match".split()

    def make_coro(pattern):
        def coro():
            line = ''
            while True:
                m = re.search(pattern, line)
                if m:
                    line = yield pattern
                else:
                    line = yield None

        return coro

    pat1 = r'pa+ttern'
    coro = make_coro(pat1)
    gr = utilities.get_records(lines, [coro])
    assert list(gr) == [pat1] * 2

    pat2 = r'^no_ma\w*$'
    coro2 = make_coro(pat2)

    gr = utilities.get_records(lines, [coro, coro2])
    assert list(gr) == ([pat1] * 2) + [pat2]


def test_get_os_from_agents():
    agent_strings = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
        'non standard agent string', None
    ]
    agent_strings = [{'user_agent': s} for s in agent_strings]
    parsed = list(utilities.get_os_from_agents(agent_strings))
    assert parsed[0]['os'] == 'Windows NT 6.1; WOW64; rv:28.0'
    assert parsed[1]['os'] == ''


def test_parse_generic_log_line():
    line = r'75.130.202.179 - - [13/Nov/2014:19:38:49] "GET /get/azw3/The Slow Regard of Silent Things (Tales From Temerant) - Patrick Rothfuss_16638.azw3 HTTP/1.1" 200 4215864 "http://localhost:8080/browse/category/newest" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0"'
    result = utilities.parse_generic_server_log_line([line])
    parsed = {
        'host':       '75.130.202.179',
        'identity':   '-',
        'user':       '-',
        'datetime':   datetime.datetime(2014, 11, 13, 19, 38, 49),
        'timezone':   None,
        'method':     'GET',
        'request':    '/get/azw3/The Slow Regard of Silent Things (Tales From Temerant) - Patrick Rothfuss_16638.azw3',
        'protocol':   'HTTP/1.1',
        'status':     200,
        'bytes':      4215864,
        'referer':    'http://localhost:8080/browse/category/newest',
        'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
    }  # yapf: disable
    assert next(result) == parsed


def test_parse_v3_log_line():
    line = r'192.168.0.1 port-56702 - 29/Jul/2017:09:26:37 -0700 "GET /get/cover/21469/Calibre_Library HTTP/1.1" 200 459389'
    result = utilities.parse_generic_server_log_line([line])
    parsed = {
        'host':       '192.168.0.1',
        'identity':   'port-56702',
        'user':       '-',
        'datetime':   datetime.datetime(2017, 7, 29, 9, 26, 37),
        'timezone':   '-0700 ',
        'method':     'GET',
        'request':    '/get/cover/21469/Calibre_Library',
        'protocol':   'HTTP/1.1',
        'status':     200,
        'bytes':      459389,
        'referer':    None,
        'user_agent': None,
    }  # yapf: disable
    assert next(result) == parsed

def test_parse_v3_log_line_string_status():
    line = r'192.168.0.1 port-41176 - 15/Nov/2020:10:02:46 -0800 "GET /get/cover/17524/Calibre_Library HTTP/1.1" HTTPStatus.NOT_MODIFIED 135'
    result = utilities.parse_generic_server_log_line([line])
    parsed = {
        'host':       '192.168.0.1',
        'identity':   'port-41176',
        'user':       '-',
        'datetime':   datetime.datetime(2020, 11, 15, 10, 2, 46),
        'timezone':   '-0800 ',
        'method':     'GET',
        'request':    '/get/cover/17524/Calibre_Library',
        'protocol':   'HTTP/1.1',
        'status':     'HTTPStatus.NOT_MODIFIED',
        'bytes':      135,
        'referer':    None,
        'user_agent': None,
    }  # yapf: disable
    assert next(result) == parsed


def test_coro_from_gen():
    def square(nums):
        for n in nums:
            yield n * n

    coro = utilities.coro_from_gen(square)
    next(coro)
    results = [coro.send(x) for x in range(10)]
    assert results == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


def test_get_locations():
    mock_ipdb = mock.MagicMock()

    data = {
        'city': {
            'geoname_id': 5045360,
            'names': {
                'en': 'Saint Paul',
            }
        },
        'continent': {
            'code': 'NA',
            'geoname_id': 6255149,
            'names': {
                'en': 'North America',
            }
        },
        'country': {
            'geoname_id': 6252001,
            'iso_code': 'US',
            'names': {
                'en': 'United States',
            }
        },
        'location': {
            'accuracy_radius': 20,
            'latitude': 44.9532,
            'longitude': -93.158,
            'metro_code': 613,
            'time_zone': 'America/Chicago'
        },
        'postal': {
            'code': '55104'
        },
        'registered_country': {
            'geoname_id': 6252001,
            'iso_code': 'US',
            'names': {
                'en': 'United States',
            }
        },
        'subdivisions': [{
            'geoname_id': 5037779,
            'iso_code': 'MN',
            'names': {
                'es': 'Minnesota',
            }
        }],
        'traits': {
            'ip_address': '128.101.101.101'
        }
    }

    sample_record = geoip2.models.City(data, ['en'])
    mock_ipdb.city = mock.Mock(return_value=None, side_effect=AddressNotFoundError())
    ips = [{'host': str(i)} for i in range(3)]
    loc = utilities.get_locations(ips, mock_ipdb)
    assert next(loc)['location'] == 'NONE, NONE'
    mock_ipdb.city = mock.Mock(return_value=sample_record)
    assert next(loc)['location'] == 'Saint Paul, MN'


def test_time_filter():
    record1 = {
        'host': '1',
        'type': 'download',
        'user_agent': 'agent',
        'info': 'dresden files',
        'datetime': datetime.datetime.now()
    }
    record2 = copy.deepcopy(record1)
    record2['datetime'] = record2['datetime'] + datetime.timedelta(20)
    record3 = copy.deepcopy(record2)
    record3['info'] = 'another file'
    record4 = copy.deepcopy(record3)
    record4['type'] = 'search'

    records = [record1, record2, record3, record4]
    assert len(list(utilities.time_filter(records, 10))) == 4
    assert len(list(utilities.time_filter(records, 25))) == 3


def test_resolve_book_ids(mock_db_file):
    record = {
        'host':       '192.168.0.1',
        'identity':   'port-56702',
        'user':       '-',
        'datetime':   datetime.datetime(2017, 7, 29, 9, 26, 37),
        'timezone':   '-0700 ',
        'method':     'GET',
        'request':    '/get/cover/21469/Calibre_Library',
        'protocol':   'HTTP/1.1',
        'status':     200,
        'bytes':      459389,
        'referer':    None,
        'user_agent': None,
        'file':       None,
        'book_id':    '1',
        'info': 'Book ID: 1'
    }  # yapf: disable

    resolve = utilities.resolve_book_ids([record], mock_db_file)
    assert next(resolve)['info'] == 'Book One - Author One'


def test_resolve_id_w_no_id(mock_db_file):
    record = {
        'host':       '192.168.0.1',
        'identity':   'port-56702',
        'user':       '-',
        'datetime':   datetime.datetime(2017, 7, 29, 9, 26, 37),
        'timezone':   '-0700 ',
        'method':     'GET',
        'request':    '/get/cover/21469/Calibre_Library',
        'protocol':   'HTTP/1.1',
        'status':     200,
        'bytes':      459389,
        'referer':    None,
        'user_agent': None,
        'file':       None,
        'info': 'Book ID: 1'
    }  # yapf: disable

    resolve = utilities.resolve_book_ids([record], mock_db_file)
    assert next(resolve) == record
