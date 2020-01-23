from __future__ import unicode_literals
__author__ = 'laharah'

import pytest
import shutil
import sys
import sqlite3
import os
import gzip
import tempfile
import httpretty
import tarfile
import contextlib
import platform
from io import BytesIO

import pytest

from mock_sql import SQL
import calibre_access.calibre_access as calibre_access


@contextlib.contextmanager
def temp_user_dir():
    old_user_dir = calibre_access.USER_DIR
    calibre_access.USER_DIR = tempfile.mkdtemp(prefix='calibre_access')
    yield calibre_access.USER_DIR
    shutil.rmtree(calibre_access.USER_DIR)
    calibre_access.USER_DIR = old_user_dir


@pytest.yield_fixture
def user_expansion(monkeypatch):
    path = tempfile.mkdtemp()

    def new_expand_user(p):
        return p.replace('~', path)

    monkeypatch.setattr('os.path.expanduser', new_expand_user)
    monkeypatch.setenv('APPDATA', path)
    yield path


@pytest.yield_fixture
def mock_geolite_dat():
    with temp_user_dir() as temp_user:
        path = os.path.join(temp_user, 'GeoLite2-City.mmdb')
        with open(path, 'w') as fout:
            fout.write('Fake Data...')
        yield path
        os.remove(path)


@pytest.yield_fixture
def mock_access_logs_default(request, user_expansion):
    base_path = calibre_access.get_search_dir()
    with create_logs(base_path=base_path) as file_paths:
        yield file_paths


@pytest.yield_fixture
def mock_access_logs_local(tmpdir):
    p = tmpdir
    old = p.chdir()
    try:
        with create_logs() as file_paths:
            yield file_paths
    finally:
        old.chdir()


@contextlib.contextmanager
def create_logs(base_path=None):
    file_paths = [
        'server_access_log.txt', 'server_access_log.txt.1', 'server_access_log.txt.2.gz',
        'server_access_log.txt.3.gz'
    ]
    if base_path:
        os.makedirs(base_path)
        file_paths = [os.path.join(base_path, p) for p in file_paths]
    for path in file_paths:
        if path.endswith('gz'):
            with gzip.open(path, mode='wt') as fout:
                fout.write('fake access data\nfake access data\n')
        else:
            with open(path, 'w') as fout:
                fout.write('fake access data\nfake access data\n')
    try:
        yield list(reversed(file_paths))  #reversed so newest is last
    finally:
        for path in file_paths:
            os.remove(path)
        if base_path:
            try:
                os.removedirs(base_path)
            except FileNotFoundError:
                pass


@pytest.yield_fixture
def mock_geolite_download():
    httpretty.enable()
    sout = BytesIO()
    with tempfile.TemporaryFile() as mockfile:
        mockfile.write(b'Mocked geolite data...')
        mockfile.seek(0)
        with tarfile.open(fileobj=sout, mode='w:gz') as f:
            f.addfile(
                f.gettarinfo(fileobj=mockfile,
                             arcname='GeoLite2-City_20190205/GeoLite2-Cirt.mmdb'),
                mockfile)

    httpretty.register_uri(
        httpretty.GET,
        'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=1234&suffix=tar.gz',
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


@pytest.yield_fixture(scope='module')
def mock_db_file():
    td = tempfile.mkdtemp()
    mock_db = os.path.join(td, 'metadata.db')
    con = sqlite3.connect(mock_db)
    cur = con.cursor()
    cur.executescript(SQL)
    cur.close()
    con.close()
    try:
        yield mock_db
    finally:
        shutil.rmtree(td)
