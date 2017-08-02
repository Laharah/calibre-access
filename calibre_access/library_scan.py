import sys
import re
if sys.version_info.major == 3:
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
