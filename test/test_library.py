import sqlite3
import pytest
import os
import tempfile
import shutil

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


def test_get_cursor(mock_db_file):
    c = lb.get_cursor(mock_db_file)
    assert c.execute("SELECT title from books where id = 1").fetchone() == ('Book One',)
