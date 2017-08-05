import sqlite3


class BookLibrary(object):
    """a context wrapper for calibre-db lookups"""

    def __init__(self, db_file):
        self.db_file = db_file
        self.con = None
        self.cur = None

    def __enter__(self):
        try:
            self.con = sqlite3.connect('file:{}?mode=ro'.format(self.db_file), uri=True)
        except TypeError:
            self.con = sqlite3.connect(self.db_file)  # URI only supported py >= 3.4

        self.cur = self.con.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        self.con.close()

    def __getitem__(self, index):
        assert self.con is not None and self.cur is not None
        self.cur.execute('SELECT title FROM books WHERE id = ?', (index, ))
        try:
            return self.cur.fetchone()[0]
        except TypeError:
            raise KeyError(str(index))
