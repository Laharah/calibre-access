from __future__ import unicode_literals
__author__ = 'laharah'

import tempfile
import os
import contextlib
import shutil
import gzip
from io import BytesIO
import platform

import pytest
import mock
import httpretty

import calibre_access.calibre_access as calibre_access
import calibre_access.utilities as utilities


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
def mock_access_log(request):
    file_path = getattr(request.function, 'mock_log_path', 'server_access_log.txt')
    with open(file_path, 'w') as fout:
        fout.write('fake access data')
    yield file_path
    os.remove(file_path)


@pytest.yield_fixture
def mock_geolite_download():
    httpretty.enable()
    sout = BytesIO()
    with gzip.GzipFile(fileobj=sout, mode='wb') as f:
        f.write(b'Mocked geolite data...')

    httpretty.register_uri(httpretty.GET,
                           "http://geolite.maxmind.com/download/geoip/database"
                           "/GeoLiteCity.dat.gz",
                           body=sout.getvalue(), status=200)
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


def test_download_database(mock_geolite_download):
    with temp_user_dir():
        shutil.rmtree(calibre_access.USER_DIR)
        assert calibre_access.download_database() == os.path.join(
            calibre_access.USER_DIR, 'GeoLiteCity.dat')
        assert os.path.exists(calibre_access.USER_DIR)
        assert not os.path.exists(os.path.join(calibre_access.USER_DIR,
                                               'GeoLiteCity.dat.gz'))
        with open(os.path.join(calibre_access.USER_DIR, 'GeoLiteCity.dat')) as fin:
            assert fin.read() == 'Mocked geolite data...'


@pytest.mark.usefixtures('mock_platform')
class TestLocateLogsOSX():
    p_form = 'Darwin'

    def test_osx(self, monkeypatch):
        monkeypatch.setattr('os.path.exists', lambda x: True)
        assert calibre_access.locate_logs() == os.path.expanduser(
            '~/Library/Preferences/calibre/server_access_log.txt')

    def test_osx_current_folder(self, mock_access_log):
        with redirect_user_expansion():
            assert calibre_access.locate_logs() == 'server_access_log.txt'

    def test_osx_missing(self):
        with redirect_user_expansion(), pytest.raises(IOError):
            calibre_access.locate_logs()


@pytest.mark.usefixtures('mock_platform')
class TestLocateLogsWindows():
    p_form = 'Windows'

    def test_windows(self, monkeypatch, mock_platform):
        monkeypatch.setattr('os.path.exists', lambda x: True)
        monkeypatch.setenv('APPDATA', '.')
        assert calibre_access.locate_logs() == os.path.join('.', 'calibre',
                                                            'server_access_log.txt')

    def test_windows_current_folder(self, monkeypatch, mock_access_log):
        monkeypatch.setenv('APPDATA', 'NON EXISTENT!')
        assert calibre_access.locate_logs() == 'server_access_log.txt'

    def test_windows_missing(self, monkeypatch):
        monkeypatch.setenv('APPDATA', 'NON EXISTENT')
        monkeypatch.setattr('os.path.exists', lambda x: False)
        with pytest.raises(IOError):
            calibre_access.locate_logs()


@pytest.mark.usefixtures('mock_platform')
class TestLocateLogslinux():
    p_form = 'Linux'

    def test_linux(self, monkeypatch):
        monkeypatch.setattr('os.path.exists', lambda x: True)
        assert calibre_access.locate_logs() == os.path.expanduser(
            '~/.config/calibre/server_access_log.txt')

    def test_linux_current_folder(self, mock_access_log):
        with redirect_user_expansion():
            assert calibre_access.locate_logs() == 'server_access_log.txt'

    def test_linux_missing(self, monkeypatch):
        monkeypatch.setattr('os.path.exists', lambda x: False)
        with pytest.raises(IOError):
            calibre_access.locate_logs()


@mock.patch('calibre_access.calibre_access.pygeoip.GeoIP', autospec=True)
class TestGetDatabase():

    def test_missing_dat(self, mock_geo, mock_geolite_download):
        with temp_user_dir():
            result = calibre_access.get_database()
            assert result == mock_geo.return_value

    def test_current_dat(self, mock_geo, mock_geolite_dat):
        assert calibre_access.get_database() == mock_geo.return_value

    def test_dat_too_old(self, mock_geo, mock_geolite_dat, mock_geolite_download):
        t = os.path.getmtime(mock_geolite_dat)
        t -= 2628000
        os.utime(mock_geolite_dat, (t,t))
        result = calibre_access.get_database()
        assert result == mock_geo.return_value
        assert os.path.getmtime(mock_geolite_dat) - t >= 2628000

    def test_old_dat_no_download(self, mock_geo, mock_geolite_dat, monkeypatch):

        def error_download():
            raise calibre_access.requests.ConnectionError('no internet')

        monkeypatch.setattr('calibre_access.calibre_access.download_database', error_download)
        t = os.path.getmtime(mock_geolite_dat)
        t -= 2628000
        os.utime(mock_geolite_dat, (t, t))
        result = calibre_access.get_database()
        assert result == mock_geo.return_value
        assert abs(os.path.getmtime(mock_geolite_dat) - t) < 1

def test_search_coro():
    coro = calibre_access.search_coro()
    next(coro)
    line = '166.147.101.20 - - [20/Oct/2014:08:18:26] "GET /browse/search?query=dresden+files HTTP/1.1" 200 7814 "http://localhost:8080/browse/search?query=iron+druid" "Mozilla/5.0 (Linux; U; Android 4.2.2; en-us; KFAPWI Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.32 like Chrome/34.0.1847.137 Safari/537.36"'
    result = coro.send(line)
    assert result['host'] == '166.147.101.20'
    assert result['query'] == 'dresden+files'
    assert result['type'] == 'search'
    assert result['info'] == result['query']

    line = 'this is not a search line'
    assert coro.send(line) is None

def test_download_coro():
    coro = calibre_access.download_coro()
    next(coro)
    line = '24.1.110.218 - - [05/Dec/2014:18:54:19] "GET /get/mobi/Devil Said Bang - Richard Kadrey_16536.mobi HTTP/1.1" 200 531748 "http://localhost:8080/browse/search?query=sandman+slim" "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFAPWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.40 like Chrome/37.0.2026.117 Safari/537.36"'
    result = coro.send(line)
    assert result['host'] == '24.1.110.218'
    assert result['file'] == 'Devil Said Bang - Richard Kadrey_16536.mobi'
    assert result['type'] == 'download'
    assert result['info'] == 'Devil Said Bang - Richard Kadrey_16536.mobi'

    assert coro.send('this is not a download line') is None

def test_seperate_search_download():
    search = '166.147.101.20 - - [20/Oct/2014:08:18:26] "GET /browse/search?query=dresden+files HTTP/1.1" 200 7814 "http://localhost:8080/browse/search?query=iron+druid" "Mozilla/5.0 (Linux; U; Android 4.2.2; en-us; KFAPWI Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.32 like Chrome/34.0.1847.137 Safari/537.36"'
    download = '24.1.110.218 - - [05/Dec/2014:18:54:19] "GET /get/mobi/Devil Said Bang - Richard Kadrey_16536.mobi HTTP/1.1" 200 531748 "http://localhost:8080/browse/search?query=sandman+slim" "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFAPWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.40 like Chrome/37.0.2026.117 Safari/537.36"'
    lines = [search, download]
    coros = calibre_access.search_coro, calibre_access.download_coro
    results = list(utilities.get_records(lines, coros))
    assert len(results) == 2
    assert results[0]['type'] == 'search'
    assert results[1]['type'] == 'download'

if __name__ == '__main__':
    pytest.main()
