__author__ = 'laharah'

import tempfile
import os
import contextlib
import shutil
import gzip
import StringIO
import platform

import pytest
import mock
import httpretty

import calibre_access



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
def mock_access_log(request):
    print dir(request)
    file_path = getattr(request.function, 'mock_log_path', 'server_access_log.txt')
    with open(file_path, 'w') as fout:
        fout.write('fake access data')
    yield file_path
    os.remove(file_path)


@pytest.yield_fixture
def mock_geolite_download():
    httpretty.enable()
    sout = StringIO.StringIO()
    with gzip.GzipFile(fileobj=sout, mode='w') as f:
        f.write('Mocked geolite data...')

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
    # TODO: use pytest monkey patch to path exsists and expand user
    p_form = 'Darwin'
    tmp_dir = tempfile.mkdtemp()

    def test_osx(self, mock_platform, mock_access_log):
        assert calibre_access.locate_logs() == TestLocateLogsOSX.mock_log_path

    def test_osx_current_folder(self, mock_platform, mock_access_log):
        p_form = 'Darwin'
        with redirect_user_expansion(TestLocateLogsOSX.tmp_dir):
            assert calibre_access.locate_logs() == 'server_access_log.txt'

    def test_osx_missing(self, mock_platform):
        with redirect_user_expansion(), pytest.raises(IOError):
            calibre_access.locate_logs()






pytest.main()