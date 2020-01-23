from __future__ import unicode_literals
__author__ = 'laharah'

import pytest
import glob
import math
import mock
import os
import shutil

from fixtures import *
import httpretty

import calibre_access.calibre_access as calibre_access
import calibre_access.utilities as utilities


def test_download_database(mock_geolite_download):
    with temp_user_dir():
        shutil.rmtree(calibre_access.USER_DIR)
        assert calibre_access.download_database(1234) == os.path.join(
            calibre_access.USER_DIR, 'GeoLite2-City.mmdb')
        assert os.path.exists(calibre_access.USER_DIR)
        assert not glob.glob(
            os.path.join(calibre_access.USER_DIR, 'GeoLite2-City*.tar.gz'))
        with open(os.path.join(calibre_access.USER_DIR, 'GeoLite2-City.mmdb')) as fin:
            assert fin.read() == 'Mocked geolite data...'


@pytest.mark.usefixtures('mock_platform')
class TestLocateLogsOSX():
    p_form = 'Darwin'

    def test_get_search_dir(self):
        assert calibre_access.get_search_dir() == os.path.expanduser(
            '~/Library/Preferences/calibre')

    def test_osx(self, mock_access_logs_default):
        assert calibre_access.locate_logs() == mock_access_logs_default

    def test_osx_current_folder(self, mock_access_logs_local, user_expansion):
        assert calibre_access.locate_logs() == mock_access_logs_local

    def test_osx_missing(self, user_expansion, tmpdir):
        p = tmpdir.chdir()
        try:
            with pytest.raises(IOError):
                print(calibre_access.locate_logs())
        finally:
            p.chdir()


@pytest.mark.usefixtures('mock_platform')
class TestLocateLogsWindows():
    p_form = 'Windows'

    def test_get_search_dir(self, monkeypatch, user_expansion):
        assert calibre_access.get_search_dir() == os.path.join(user_expansion, 'calibre')

    def test_windows(self, monkeypatch, mock_access_logs_default):
        assert calibre_access.locate_logs() == mock_access_logs_default

    def test_windows_current_folder(self, monkeypatch, mock_access_logs_local):
        monkeypatch.setenv('APPDATA', 'NON EXISTENT!')
        assert calibre_access.locate_logs() == mock_access_logs_local

    def test_windows_missing(self, monkeypatch, tmpdir):
        try:
            p = tmpdir.chdir()
            monkeypatch.setenv('APPDATA', 'NON EXISTENT')
            with pytest.raises(IOError):
                calibre_access.locate_logs()
        finally:
            p.chdir()


@pytest.mark.usefixtures('mock_platform')
class TestLocateLogslinux():
    p_form = 'Linux'

    def test_get_search_dir(self):
        assert calibre_access.get_search_dir() == os.path.expanduser('~/.config/calibre')

    def test_linux(self, mock_access_logs_default):
        assert calibre_access.locate_logs() == mock_access_logs_default

    def test_linux_current_folder(self, mock_access_logs_local, user_expansion):
        assert calibre_access.locate_logs() == mock_access_logs_local

    def test_linux_missing(self, user_expansion, tmpdir):
        p = tmpdir.chdir()
        try:
            with pytest.raises(IOError):
                calibre_access.locate_logs()
        finally:
            p.chdir()


@mock.patch('calibre_access.calibre_access.geoip2.database.Reader', autospec=True)
class TestGetDatabase():
    def test_missing_dat(self, mock_geo, mock_geolite_download):
        with temp_user_dir():
            result = calibre_access.get_database(maxmind_license=1234)
            assert result == mock_geo.return_value

    def test_current_dat(self, mock_geo, mock_geolite_dat):
        assert calibre_access.get_database(maxmind_license=1234) == mock_geo.return_value

    def test_dat_too_old(self, mock_geo, mock_geolite_dat, mock_geolite_download):
        t = os.path.getmtime(mock_geolite_dat)
        t -= 2628000
        os.utime(mock_geolite_dat, (t, t))
        result = calibre_access.get_database(maxmind_license=1234)
        print(os.listdir(os.path.dirname(mock_geolite_dat)))
        assert result == mock_geo.return_value
        assert os.path.getmtime(mock_geolite_dat) - math.floor(t) >= 2628000

    def test_old_dat_no_download(self, mock_geo, mock_geolite_dat, monkeypatch):
        def error_download(license):
            raise calibre_access.requests.ConnectionError('no internet')

        monkeypatch.setattr('calibre_access.calibre_access.download_database',
                            error_download)
        t = os.path.getmtime(mock_geolite_dat)
        t -= 2628000
        os.utime(mock_geolite_dat, (t, t))
        with pytest.warns(UserWarning):
            result = calibre_access.get_database(maxmind_license=1234)
        assert result == mock_geo.return_value
        assert abs(os.path.getmtime(mock_geolite_dat) - t) < 1

    @pytest.mark.skipif(sys.version_info < (3, 4), reason="mock problem")
    def test_force_refresh(self, mock_geo, mock_geolite_dat, mock_geolite_download):
        # httpretty.reset()
        # assert httpretty.has_request() == False
        result = calibre_access.get_database(maxmind_license=1234, force_refresh=True)
        assert result == mock_geo.return_value
        assert httpretty.has_request() == True


def test_search_coro():
    coro = calibre_access.search_coro()
    next(coro)
    line = '166.147.101.20 - - [20/Oct/2014:08:18:26] "GET /browse/search?query=dresden+files HTTP/1.1" 200 7814 "http://localhost:8080/browse/search?query=iron+druid" "Mozilla/5.0 (Linux; U; Android 4.2.2; en-us; KFAPWI Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.32 like Chrome/34.0.1847.137 Safari/537.36"'
    result = coro.send(line)
    assert result['host'] == '166.147.101.20'
    assert result['query'] == 'dresden files'
    assert result['type'] == 'search'
    assert result['info'] == result['query']

    line = 'this is not a search line'
    assert coro.send(line) is None


def test_search_coro_with_v3():
    coro = calibre_access.search_coro()
    next(coro)
    line = '192.168.0.1 port-56768 - 29/Jul/2017:09:33:53 -0700 "GET /interface-data/books-init?library_id=Calibre_Library&search=authors:%22%3DTom%20Babin%22&sort=timestamp.desc&1501346031589 HTTP/1.1" 200 -'
    result = coro.send(line)
    assert result['host'] == '192.168.0.1'
    assert result['query'] == 'authors:"=Tom Babin"'
    assert result['type'] == 'search'
    assert result['info'] == result['query']


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


def test_download_coro_with_v3():
    coro = calibre_access.download_coro()
    next(coro)
    line = '192.168.0.1 port-56702 - 29/Jul/2017:09:26:52 -0700 "GET /get/MOBI/21468/Calibre_Library HTTP/1.1" 200 4252028'
    result = coro.send(line)
    assert result['host'] == '192.168.0.1'
    assert result['file'] == None
    assert result['book_id'] == '21468'
    assert result['type'] == 'download'


def test_download_coro_v3_legacy():
    coro = calibre_access.download_coro()
    next(coro)
    line = '52.207.254.44 port-49702 - 19/Aug/2017:15:10:28 -0700 "GET /legacy/get/MOBI/21474/Calibre_Library/Meddling%20Kids%20-%20Edgar%20Cantero_21474.mobi HTTP/1.1" 200 2747777'
    result = coro.send(line)
    assert result['host'] == '52.207.254.44'
    assert result['file'] == None
    assert result['book_id'] == '21474'
    assert result['type'] == 'download'


def test_read_coro():
    coro = calibre_access.read_coro()
    next(coro)
    line = '192.168.0.1 port-56919 - 29/Jul/2017:09:40:44 -0700 "GET /book-manifest/21470/EPUB?library_id=Calibre_Library&1501346444609 HTTP/1.1" 200 -'
    result = coro.send(line)
    assert result['host'] == '192.168.0.1'
    assert result['book_id'] == '21470'
    assert result['type'] == 'read'


def test_view_coro():
    coro = calibre_access.view_coro()
    next(coro)
    line = '192.168.0.1 port-56702 - 29/Jul/2017:09:26:37 -0700 "GET /get/cover/21469/Calibre_Library HTTP/1.1" 200 459389'
    result = coro.send(line)
    assert result['host'] == '192.168.0.1'
    assert result['book_id'] == '21469'
    assert result['type'] == 'view'

    line = '192.168.0.1 port-56921 - 29/Jul/2017:09:40:44 -0700 "GET /get/cover/21470/Calibre_Library?library_id=Calibre_Library&1501346444650 HTTP/1.1" 200 122618'
    result = coro.send(line)
    assert not result


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
