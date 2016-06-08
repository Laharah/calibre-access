from __future__ import unicode_literals, absolute_import

import calibre_access.utilities as utilities
import re
import datetime
import mock
import copy


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
        'non standard agent string',
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
        'method':     'GET',
        'request':    '/get/azw3/The Slow Regard of Silent Things (Tales From Temerant) - Patrick Rothfuss_16638.azw3',
        'protocol':   'HTTP/1.1',
        'status':     200,
        'bytes':      4215864,
        'referer':    'http://localhost:8080/browse/category/newest',
        'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
    }
    assert next(result) == parsed

def test_coro_from_gen():
    def square(nums):
        for n in nums:
            yield n*n

    coro = utilities.coro_from_gen(square)
    next(coro)
    results = [coro.send(x) for x in range(10)]
    assert results == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


def test_get_locations():
    mock_ipdb = mock.MagicMock()
    rec = {'area_code': 828,
           'city':          'Asheville',
           'continent':     'NA',
           'country_code':  'US',
           'country_code3': 'USA',
           'country_name':  'United States',
           'dma_code':      567,
           'latitude':      35.568299999999994,
           'longitude':     -82.6272,
           'metro_code':    'Greenville-Spartenburg, SC',
           'postal_code':   '28806',
           'region_code':   'NC',
           'time_zone':     'America/New_York'}

    mock_ipdb.record_by_addr = mock.Mock(return_value=None)
    ips = [{'host':str(i)} for i in range(3)]
    loc = utilities.get_locations(ips, mock_ipdb)
    assert next(loc)['location'] == 'NONE, NONE'
    mock_ipdb.record_by_addr = mock.Mock(return_value=rec)
    assert next(loc)['location'] == 'Asheville, NC'
    rec['region_code'] = None
    assert next(loc)['location'] == 'United States'

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
