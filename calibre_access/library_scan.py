import sys
import re
import json

if sys.version_info > (3, 5):
    from pathlib import Path
else:
    from pathlib2 import Path


def scan_lib(libpath):
    libpath = Path(libpath)
    book_pat = re.compile(r'^(.*) \((\d+)\)$')
    books = {}
    for author in libpath.iterdir():
        if not author.is_dir():
            continue
        for folder in author.iterdir():
            try:
                title, id = book_pat.match(folder.name).groups()
            except AttributeError:
                continue

            books[id] = title
    return books


def write_cache(lib_ids, fout):
    with open(fout, 'w') as f:
        json.dump(lib_ids, f)


def load_cache(cache_file):
    with open(cache_file, 'r') as f:
        return json.load(f)
