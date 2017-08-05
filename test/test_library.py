import sqlite3
import pytest
import os
import tempfile
import shutil
import hashlib
import sys

from mock_sql import SQL
import calibre_access.library as lb


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


def test_book_library_instantiation(mock_db_file):
    bl = lb.BookLibrary(mock_db_file)


def test_book_library_lookup(mock_db_file):
    with lb.BookLibrary(mock_db_file) as bl:
        assert bl['1'] == "Book One"
        assert bl['2'] == "Book Two"
        assert bl['4'] == "This is a Very Long Book Name That Will Be Truncated"


def test_book_library_lookup_must_be_context(mock_db_file):
    bl = lb.BookLibrary(mock_db_file)
    with pytest.raises(AssertionError):
        t = bl['1']


@pytest.mark.skipif(sys.version_info < (3, 4), reason='unsuported feature py < 3.4')
def test_assure_no_write(mock_db_file):
    with open(mock_db_file, 'rb') as f:
        h = hashlib.sha1(f.read()).hexdigest()
    with lb.BookLibrary(mock_db_file) as bl:
        with pytest.raises(sqlite3.OperationalError):
            bl.cur.execute('DROP TABLE books')
            bl.con.commit()
    with open(mock_db_file, 'rb') as f:
        assert hashlib.sha1(f.read()).hexdigest() == h


def test_bad_index_raises_key_error(mock_db_file):
    with lb.BookLibrary(mock_db_file) as bl:
        with pytest.raises(KeyError):
            bl['10'] == None


def test_no_set_index(mock_db_file):
    with lb.BookLibrary(mock_db_file) as bl, pytest.raises(TypeError):
        bl['1'] = "changed title"
