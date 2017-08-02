from __future__ import unicode_literals
__author__ = 'laharah'

import pytest
import shutil
import sys
import os
import tempfile
import httpretty
import gzip
import contextlib
import platform
from io import BytesIO

import pytest

import calibre_access.calibre_access as calibre_access

if sys.version_info > (3, 5):
    from pathlib import Path
else:
    from pathlib2 import Path


@contextlib.contextmanager
def temp_user_dir():
    old_user_dir = calibre_access.USER_DIR
    calibre_access.USER_DIR = tempfile.mkdtemp(prefix='calibre_access')
    yield calibre_access.USER_DIR
    shutil.rmtree(calibre_access.USER_DIR)
    calibre_access.USER_DIR = old_user_dir


@pytest.yield_fixture
def mock_lib_dir():
    td = tempfile.mkdtemp()
    root = Path(td)
    meta = root / 'metadata.opf'
    meta.write_text('this is metadata')
    a1 = (root / "Author One")
    a2 = (root / "Author Two")
    b1 = (a1 / "Book One (123)")
    b2 = (a1 / "Book Two (23456)")
    b3 = (a2 / "Book Three (345)")
    for d in (a1, a2, b1, b2, b3):
        d.mkdir()
    b1m = (b1 / "Book One - Author One.mobi").write_text("mobi book 1")
    b1e = (b1 / "Book One - Author One.epub").write_text("epub book 1")
    try:
        yield root
    finally:
        shutil.rmtree(td)


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
        path = os.path.join(temp_user, 'GeoLiteCity.dat')
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
    with gzip.GzipFile(fileobj=sout, mode='wb') as f:
        f.write(b'Mocked geolite data...')

    httpretty.register_uri(
        httpretty.GET,
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
