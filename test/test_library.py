import sqlite3
import pytest
import os
import tempfile

from mock_sql import SQL
import calibre_access.library as lb

@pytest.yield_fixture(scope='module')
def mock_db_file():
    td = tempfile.TemporaryDirectory()
    mock_db = os.path.join(td.name, 'metadata.db')
    con = sqlite3.connect(mock_db)
    cur = con.cursor()
    cur.executescript(SQL)
    cur.close()
    con.close()
    yield mock_db


def test_get_cursor(mock_db_file):
    c = lb.get_cursor(mock_db_file)
    print(mock_db_file)
    assert c.execute("SELECT title from books where id = 1").fetchone() == ('Book One',)

def test_get_cursor2(mock_db_file):
    c = lb.get_cursor(mock_db_file)
    print(mock_db_file)
