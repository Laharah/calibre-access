import pytest
import calibre_access.library_scan as ls
import sys
from fixtures import mock_lib_dir

if sys.version_info.major == 3:
    from pathlib import Path
else:
    from pathlib2 import Path

BOOK_IDS = {'123': 'Book One', '23456': 'Book Two', '345': 'Book Three'}

def test_scan_lib(mock_lib_dir):
    ids = ls.scan_lib(mock_lib_dir)
    assert ids == BOOK_IDS


def test_scan_lib_str(mock_lib_dir):
    ids = ls.scan_lib(mock_lib_dir.absolute())
    assert ids == BOOK_IDS
