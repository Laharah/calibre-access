from __future__ import print_function, unicode_literals

import re
import gzip
import datetime
from .library import BookLibrary


def get_lines_from_logs(logs):
    """
    Given a series of log files, yield one line at a time from them.
    Args:
        logs: iterable of log files in text or gzip format
    """
    for log in logs:
        if log.endswith('gz'):
            with gzip.open(log, mode='rt') as fin:
                for line in fin:
                    yield line
        else:
            with open(log) as fin:
                for line in fin:
                    yield line


def get_records(lines, coroutines):
    """
    generateor that will feed lines to coroutines and return records.
    Args:
        lines: iterator of log lines
        coroutines: list of coroutine functions for parsing the records

    Returns: a generator of records
    """
    coroutines = [coro() for coro in coroutines]
    for coro in coroutines:  # prime the coroutines
        next(coro)

    for line in lines:
        for coro in coroutines:
            record = coro.send(line)
            if record:
                yield record
    for coro in coroutines:
        coro.close()


def parse_generic_server_log_line(lines):
    logpats = re.compile(r'(\S+) (\S+) (\S+) \[?(.*?)\]? (-\d+ )?"(.*?)" (\S+) (\S+) ?(.*)?')
    request_pat = re.compile(r'(\S+) (.+) (\S+)')
    #request_line = 'method' 'request' 'protocol'
    fields = ['host', 'identity', 'user', 'datetime', 'timezone', 'request_line',
              'status', 'bytes', 'ref/uagent']
    for line in lines:
        data = [g for g in logpats.match(line).groups()]
        d = dict(zip(fields, data))
        try:
            req = request_pat.match(d['request_line'])
            d['method'], d['request'], d['protocol'] = req.groups()
        except AttributeError:
            d['method'], d['request'], d['protocol'] = None, None, None
        finally:
            del d['request_line']
        if d['ref/uagent']:
            d['referer'], d['user_agent'] = re.findall(r'"(.*?)"', d['ref/uagent'])
        else:
            d['referer'], d['user_agent'] = None, None
        del d['ref/uagent']
        field_map = {
            'status': lambda x: int(x),
            'bytes': lambda s: int(s) if s != '-' else 0,
            'datetime': lambda s: datetime.datetime.strptime(s, '%d/%b/%Y:%H:%M:%S'),
        }

        for field, func in field_map.items():
            d[field] = func(d[field])
        yield d


def get_os_from_agents(records):
    pat = re.compile(r'\S+ \((.+)\).*')
    for record in records:
        try:
            m = pat.match(record['user_agent'])
        except TypeError:
            record['os'] = ''
        else:
            record['os'] = m.group(1) if m else ''
        yield record


def coro_from_gen(generator):
    """turn a normal generator into a coroutine"""

    def input_pipe():
        """small internal coroutine that recieves data"""
        x = ''
        while True:
            x = yield x
            yield  # to keep the generator in lock step with input

    pipe = input_pipe()
    next(pipe)  # prime the input coroutune
    gen = generator(pipe)
    n = yield  # get first item
    while True:
        pipe.send(n)
        n = yield next(gen)


def get_locations(records, ipdatabase):
    cache = {}
    for record in records:
        ip = record['host']
        try:
            loc = cache[ip]
        except KeyError:
            loc = ipdatabase.record_by_addr(ip)
            cache[ip] = loc
        if not loc:
            loc = {'city': "NONE", 'region_code': "NONE"}
        try:
            loc_string = ', '.join([loc['city'], loc['region_code']])
        except TypeError:
            loc_string = loc['country_name']
        record['location'] = loc_string
        yield record


def time_filter(records, seconds):
    """filters identical records who's time differs by less than x seconds"""
    delta = datetime.timedelta(seconds)
    records = iter(records)
    previous = next(records)
    yield previous
    current = None
    fields = ['host', 'type', 'user_agent', 'info']

    for record in records:
        current = record
        for field in fields:
            if current[field] != previous[field]:
                yield current
                break
        else:
            if previous['datetime'] + delta < current['datetime']:
                yield current

        previous = current

def resolve_book_ids(records, library_db):
    with BookLibrary(library_db) as lib:
        for record in records:
            try:
                record['info'] = lib[record['book_id']]
            except KeyError:
                pass
            yield record
