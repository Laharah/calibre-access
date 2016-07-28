from __future__ import unicode_literals
__author__ = 'laharah'

import pytest
import shutil
import os
import tempfile
import httpretty
import gzip
import contextlib
import platform
from io import BytesIO

import calibre_access.calibre_access as calibre_access


@contextlib.contextmanager
def temp_user_dir():
    old_user_dir = calibre_access.USER_DIR
    calibre_access.USER_DIR = tempfile.mkdtemp(prefix='calibre_access')
    yield calibre_access.USER_DIR
    shutil.rmtree(calibre_access.USER_DIR)
    calibre_access.USER_DIR = old_user_dir


@contextlib.contextmanager
def redirect_user_expansion(path=None):
    old = os.path.expanduser
    path = tempfile.mkdtemp() if path is None else path

    def new_expand_user(p):
        return p.replace('~', path)

    os.path.expanduser = new_expand_user
    yield path
    os.path.expanduser = old
    shutil.rmtree(path)


@pytest.yield_fixture
def mock_geolite_dat():
    with temp_user_dir() as temp_user:
        path = os.path.join(temp_user, 'GeoLiteCity.dat')
        with open(path, 'w') as fout:
            fout.write('Fake Data...')
        yield path
        os.remove(path)


@pytest.yield_fixture
def mock_access_logs_default(request, mock_platform, monkeypatch):
    monkeypatch.setenv('APPDATA', '.')
    with redirect_user_expansion():
        base_path = calibre_access.get_search_dir()
        with create_logs(base_path=base_path) as file_paths:
            yield file_paths


@pytest.yield_fixture
def mock_access_logs_local():
    with create_logs() as file_paths:
        yield file_paths


@contextlib.contextmanager
def create_logs(base_path=None):
    file_paths = ['server_access_log.txt', 'server_access_log.txt.1',
                  'server_access_log.txt.2.gz', 'server_access_log.txt.3.gz']
    for path in file_paths:
        if base_path:
            os.path.join(base_path, path)
        if not path.endswith('gz'):
            with open(path, 'w') as fout:
                fout.write('fake access data\nfake access data\n')
        else:
            with gzip.open(path, mode='wt') as fout:
                fout.write('fake access data\nfake access data\n')
    try:
        yield file_paths
    finally:
        for path in file_paths:
            os.remove(path)


@pytest.yield_fixture
def mock_geolite_download():
    httpretty.enable()
    sout = BytesIO()
    with gzip.GzipFile(fileobj=sout, mode='wb') as f:
        f.write(b'Mocked geolite data...')

    httpretty.register_uri(httpretty.GET,
                           "http://geolite.maxmind.com/download/geoip/database"
                           "/GeoLiteCity.dat.gz",
                           body=sout.getvalue(),
                           status=200)
    yield
    httpretty.disable()


@pytest.yield_fixture
def mock_platform(request):
    old = platform.system

    def mock_platform():
        return getattr(request.cls, 'p_form', 'Linux')

    platform.system = mock_platform
    yield
    platform.system = old
