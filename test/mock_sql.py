SQL = """PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE authors ( id   INTEGER PRIMARY KEY,
                              name TEXT NOT NULL COLLATE NOCASE,
                              sort TEXT COLLATE NOCASE,
                              link TEXT NOT NULL DEFAULT "",
                              UNIQUE(name)
                             );
INSERT INTO "authors" VALUES(1,'Author One','One, Author','');
INSERT INTO "authors" VALUES(2,'Author Two','Two, Author','');
INSERT INTO "authors" VALUES(5,'David Boop','Boop, David','');
INSERT INTO "authors" VALUES(6,'Larry Correia','Correia, Larry','');
INSERT INTO "authors" VALUES(7,'Maurice Broaddus','Broaddus, Maurice','');
INSERT INTO "authors" VALUES(8,'Sarah A. Hoyt','Hoyt, Sarah A.','');
INSERT INTO "authors" VALUES(9,'Alan Dean Foster','Foster, Alan Dean','');
INSERT INTO "authors" VALUES(10,'David Lee Summers','Summers, David Lee','');
INSERT INTO "authors" VALUES(11,'Kevin J. Anderson','Anderson, Kevin J.','');
INSERT INTO "authors" VALUES(12,'Naomi Brett Rourke','Rourke, Naomi Brett','');
INSERT INTO "authors" VALUES(13,'Julie Campbell','Campbell, Julie','');
INSERT INTO "authors" VALUES(14,'Peter J. Wacks','Wacks, Peter J.','');
INSERT INTO "authors" VALUES(15,'Jim Butcher','Butcher, Jim','');
INSERT INTO "authors" VALUES(16,'Jody Lynn Nye','Nye, Jody Lynn','');
INSERT INTO "authors" VALUES(17,'Sam Knight','Knight, Sam','');
INSERT INTO "authors" VALUES(18,'Robert E. Vardeman','Vardeman, Robert E.','');
INSERT INTO "authors" VALUES(19,'Phil Foglio','Foglio, Phil','');
INSERT INTO "authors" VALUES(20,'Nicole Kurtz','Kurtz, Nicole','');
INSERT INTO "authors" VALUES(21,'Michael A. Stackpole','Stackpole, Michael A.','');
INSERT INTO "authors" VALUES(22,'Bryan Thomas Schmidt','Schmidt, Bryan Thomas','');
INSERT INTO "authors" VALUES(23,'Ken Scholes','Scholes, Ken','');
CREATE TABLE books ( id      INTEGER PRIMARY KEY AUTOINCREMENT,
                             title     TEXT NOT NULL DEFAULT 'Unknown' COLLATE NOCASE,
                             sort      TEXT COLLATE NOCASE,
                             timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             pubdate   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             series_index REAL NOT NULL DEFAULT 1.0,
                             author_sort TEXT COLLATE NOCASE,
                             isbn TEXT DEFAULT "" COLLATE NOCASE,
                             lccn TEXT DEFAULT "" COLLATE NOCASE,
                             path TEXT NOT NULL DEFAULT "",
                             flags INTEGER NOT NULL DEFAULT 1,
                             uuid TEXT,
                             has_cover BOOL DEFAULT 0,
                             last_modified TIMESTAMP NOT NULL DEFAULT "2000-01-01 00:00:00+00:00");
INSERT INTO "books" VALUES(1,'Book One','Book One','2017-08-05 01:13:54.948371+00:00','0101-01-01 00:00:00+00:00',1.0,'One, Author','','','Author One/Book One (1)',1,'73500de2-ce5d-49c5-880b-7121a126bfab',0,'2017-08-05 01:14:14.022293+00:00');
INSERT INTO "books" VALUES(2,'Book Two','Book Two','2017-08-05 01:13:54.966232+00:00','0101-01-01 00:00:00+00:00',2.0,'One, Author','','','Author One/Book Two (2)',1,'b3d6c694-c493-4a33-bb14-3a7c39962116',0,'2017-08-05 01:14:19.596566+00:00');
INSERT INTO "books" VALUES(3,'Book Three','Book Three','2017-08-05 01:14:51.294581+00:00','0101-01-01 00:00:00+00:00',1.0,'Two, Author','','','Author Two/Book Three (3)',1,'21de5a04-1f15-40cb-bd8e-60885f8de85a',0,'2017-08-05 01:14:51.306863+00:00');
INSERT INTO "books" VALUES(4,'This is a Very Long Book Name That Will Be Truncated','This is a Very Long Book Name That Will Be Truncated','2017-08-05 01:40:43.351851+00:00','0101-01-01 00:00:00+00:00',1.0,'Two, Author','','','Author Two/This is a Very Long Book Name That Will Be Truncated (4)',1,'f6f9e9a5-39cf-484a-acab-750614f7f596',0,'2017-08-05 01:40:43.366170+00:00');
INSERT INTO "books" VALUES(5,'Straight Outta Tombstone (The Dresden Files - a Fistful of Warlocks)','Straight Outta Tombstone (The Dresden Files - a Fistful of Warlocks)','2017-08-05 17:15:11.197666+00:00','2017-07-04 07:00:00+00:00',1.0,'Boop, David & Correia, Larry & Broaddus, Maurice & Hoyt, Sarah A. & Foster, Alan Dean & Summers, David Lee & Anderson, Kevin J. & Rourke, Naomi Brett & Campbell, Julie & Wacks, Peter J. & Butcher, Jim & Nye, Jody Lynn & Knight, Sam & Vardeman, Robert E. & Foglio, Phil & Kurtz, Nicole & Stackpole, Michael A. & Schmidt, Bryan Thomas & Scholes, Ken','','','David Boop/Straight Outta Tombstone (The Dresden Files - a Fistful of Warlocks) (5)',1,'1688ad2b-644e-4d15-bc14-003e19e34ebf',1,'2017-08-05 17:18:47.940686+00:00');
CREATE TABLE books_authors_link ( id INTEGER PRIMARY KEY,
                                          book INTEGER NOT NULL,
                                          author INTEGER NOT NULL,
                                          UNIQUE(book, author)
                                        );
INSERT INTO "books_authors_link" VALUES(1,1,1);
INSERT INTO "books_authors_link" VALUES(2,2,1);
INSERT INTO "books_authors_link" VALUES(3,3,2);
INSERT INTO "books_authors_link" VALUES(4,4,2);
INSERT INTO "books_authors_link" VALUES(5,5,5);
INSERT INTO "books_authors_link" VALUES(6,5,6);
INSERT INTO "books_authors_link" VALUES(7,5,7);
INSERT INTO "books_authors_link" VALUES(8,5,8);
INSERT INTO "books_authors_link" VALUES(9,5,9);
INSERT INTO "books_authors_link" VALUES(10,5,10);
INSERT INTO "books_authors_link" VALUES(11,5,11);
INSERT INTO "books_authors_link" VALUES(12,5,12);
INSERT INTO "books_authors_link" VALUES(13,5,13);
INSERT INTO "books_authors_link" VALUES(14,5,14);
INSERT INTO "books_authors_link" VALUES(15,5,15);
INSERT INTO "books_authors_link" VALUES(16,5,16);
INSERT INTO "books_authors_link" VALUES(17,5,17);
INSERT INTO "books_authors_link" VALUES(18,5,18);
INSERT INTO "books_authors_link" VALUES(19,5,19);
INSERT INTO "books_authors_link" VALUES(20,5,20);
INSERT INTO "books_authors_link" VALUES(21,5,21);
INSERT INTO "books_authors_link" VALUES(22,5,22);
INSERT INTO "books_authors_link" VALUES(23,5,23);
CREATE TABLE books_languages_link ( id INTEGER PRIMARY KEY,
                                            book INTEGER NOT NULL,
                                            lang_code INTEGER NOT NULL,
                                            item_order INTEGER NOT NULL DEFAULT 0,
                                            UNIQUE(book, lang_code)
        );
INSERT INTO "books_languages_link" VALUES(1,5,1,0);
CREATE TABLE books_plugin_data(id INTEGER PRIMARY KEY,
                                     book INTEGER NOT NULL,
                                     name TEXT NOT NULL,
                                     val TEXT NOT NULL,
                                     UNIQUE(book,name));
CREATE TABLE books_publishers_link ( id INTEGER PRIMARY KEY,
                                          book INTEGER NOT NULL,
                                          publisher INTEGER NOT NULL,
                                          UNIQUE(book)
                                        );
INSERT INTO "books_publishers_link" VALUES(1,5,1);
CREATE TABLE books_ratings_link ( id INTEGER PRIMARY KEY,
                                          book INTEGER NOT NULL,
                                          rating INTEGER NOT NULL,
                                          UNIQUE(book, rating)
                                        );
INSERT INTO "books_ratings_link" VALUES(1,5,1);
CREATE TABLE books_series_link ( id INTEGER PRIMARY KEY,
                                          book INTEGER NOT NULL,
                                          series INTEGER NOT NULL,
                                          UNIQUE(book)
                                        );
INSERT INTO "books_series_link" VALUES(1,1,1);
INSERT INTO "books_series_link" VALUES(2,2,1);
CREATE TABLE books_tags_link ( id INTEGER PRIMARY KEY,
                                          book INTEGER NOT NULL,
                                          tag INTEGER NOT NULL,
                                          UNIQUE(book, tag)
                                        );
INSERT INTO "books_tags_link" VALUES(1,5,1);
INSERT INTO "books_tags_link" VALUES(2,5,2);
INSERT INTO "books_tags_link" VALUES(3,5,3);
INSERT INTO "books_tags_link" VALUES(4,5,4);
INSERT INTO "books_tags_link" VALUES(5,5,5);
CREATE TABLE comments ( id INTEGER PRIMARY KEY,
                              book INTEGER NOT NULL,
                              text TEXT NOT NULL COLLATE NOCASE,
                              UNIQUE(book)
                            );
INSERT INTO "comments" VALUES(1,5,'<p><strong>Tales of the Weird Wild West.</strong>Top authors take on the classic western, with a weird twist. Includes new stories by Larry Correia and Jim Butcher! <br>
Come visit the Old West, the land where gang initiations, ride-by shootings and territory disputes got their start. But these tales aren''t the ones your grandpappy spun around a campfire, unless he spoke of soul-sucking ghosts, steam-powered demons, and wayward aliens. <br>
Here then are seventeen stories that breathe new life in the Old West. Among them: Larry Correia explores the roots of his best-selling <em>Monster Hunter International</em> series in "Bubba Shackleford''s Professional Monster Killers." Jim Butcher reveals the origin of one of the <em>Dresden Files''</em> most popular characters in "A Fistful of Warlocks." And Kevin J. Anderson''s Dan Shamble, Zombie P.I., finds himself in a showdown in "High Midnight." Plus stories from Alan Dean Foster, Sarah A. Hoyt, Jody Lynn Nye, Michael A. Stackpole, and many more. <br>
This is a <em>new</em> Old West and you ll be lucky to get outta town alive! <br>
Contributors: <br>
David Boop<br>
Larry Correia<br>
Jody Lynn Nye<br>
Sam Knight<br>
Robert E. Vardeman<br>
Phil Foglio<br>
Nicole Kurtz<br>
Michael A. Stackpole<br>
Bryan Thomas Schmidt &amp; Ken Scholes<br>
Maurice Broaddus<br>
Sarah A. Hoyt<br>
Alan Dean Foster<br>
David Lee Summers<br>
Kevin J. Anderson<br>
Naomi Brett Rourke<br>
Julie Campbell<br>
Peter J. Wacks<br>
Jim Butcher"</p>');
CREATE TABLE conversion_options ( id INTEGER PRIMARY KEY,
                                          format TEXT NOT NULL COLLATE NOCASE,
                                          book INTEGER,
                                          data BLOB NOT NULL,
                                          UNIQUE(format,book)
                                        );
CREATE TABLE custom_columns (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    label    TEXT NOT NULL,
                    name     TEXT NOT NULL,
                    datatype TEXT NOT NULL,
                    mark_for_delete   BOOL DEFAULT 0 NOT NULL,
                    editable BOOL DEFAULT 1 NOT NULL,
                    display  TEXT DEFAULT "{}" NOT NULL,
                    is_multiple BOOL DEFAULT 0 NOT NULL,
                    normalized BOOL NOT NULL,
                    UNIQUE(label)
                );
CREATE TABLE data ( id     INTEGER PRIMARY KEY,
                            book   INTEGER NOT NULL,
                            format TEXT NOT NULL COLLATE NOCASE,
                            uncompressed_size INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            UNIQUE(book, format)
);
CREATE TABLE feeds ( id   INTEGER PRIMARY KEY,
                              title TEXT NOT NULL,
                              script TEXT NOT NULL,
                              UNIQUE(title)
                             );
CREATE TABLE identifiers  ( id     INTEGER PRIMARY KEY,
                                    book   INTEGER NOT NULL,
                                    type   TEXT NOT NULL DEFAULT "isbn" COLLATE NOCASE,
                                    val    TEXT NOT NULL COLLATE NOCASE,
                                    UNIQUE(book, type)
        );
INSERT INTO "identifiers" VALUES(1,5,'goodreads','32919692');
CREATE TABLE languages    ( id        INTEGER PRIMARY KEY,
                                    lang_code TEXT NOT NULL COLLATE NOCASE,
                                    UNIQUE(lang_code)
        );
INSERT INTO "languages" VALUES(1,'eng');
CREATE TABLE library_id ( id   INTEGER PRIMARY KEY,
                                  uuid TEXT NOT NULL,
                                  UNIQUE(uuid)
        );
INSERT INTO "library_id" VALUES(1,'5404576e-a1f3-43d2-b846-161ea6379289');
CREATE TABLE metadata_dirtied(id INTEGER PRIMARY KEY,
                             book INTEGER NOT NULL,
                             UNIQUE(book));
CREATE TABLE preferences(id INTEGER PRIMARY KEY,
                                 key TEXT NOT NULL,
                                 val TEXT NOT NULL,
                                 UNIQUE(key));
CREATE TABLE publishers ( id   INTEGER PRIMARY KEY,
                                  name TEXT NOT NULL COLLATE NOCASE,
                                  sort TEXT COLLATE NOCASE,
                                  UNIQUE(name)
                             );
INSERT INTO "publishers" VALUES(1,'Baen',NULL);
CREATE TABLE ratings ( id   INTEGER PRIMARY KEY,
                               rating INTEGER CHECK(rating > -1 AND rating < 11),
                               UNIQUE (rating)
                             );
INSERT INTO "ratings" VALUES(1,8);
CREATE TABLE series ( id   INTEGER PRIMARY KEY,
                              name TEXT NOT NULL COLLATE NOCASE,
                              sort TEXT COLLATE NOCASE,
                              UNIQUE (name)
                             );
INSERT INTO "series" VALUES(1,'Mock Series','Mock Series');
CREATE TABLE tags ( id   INTEGER PRIMARY KEY,
                            name TEXT NOT NULL COLLATE NOCASE,
                            UNIQUE (name)
                             );
INSERT INTO "tags" VALUES(1,'Urban Fantasy');
INSERT INTO "tags" VALUES(2,'Fantasy');
INSERT INTO "tags" VALUES(3,'Horror');
INSERT INTO "tags" VALUES(4,'Anthologies');
INSERT INTO "tags" VALUES(5,'Vampires');
CREATE TABLE last_read_positions ( id INTEGER PRIMARY KEY,
	book INTEGER NOT NULL,
	format TEXT NOT NULL COLLATE NOCASE,
	user TEXT NOT NULL,
	device TEXT NOT NULL,
	cfi TEXT NOT NULL,
	epoch REAL NOT NULL,
	pos_frac REAL NOT NULL DEFAULT 0,
	UNIQUE(user, device, book, format)
);
DELETE FROM sqlite_sequence;
INSERT INTO "sqlite_sequence" VALUES('books',5);
CREATE INDEX authors_idx ON books (author_sort COLLATE NOCASE);
CREATE INDEX books_authors_link_aidx ON books_authors_link (author);
CREATE INDEX books_authors_link_bidx ON books_authors_link (book);
CREATE INDEX books_idx ON books (sort COLLATE NOCASE);
CREATE INDEX books_languages_link_aidx ON books_languages_link (lang_code);
CREATE INDEX books_languages_link_bidx ON books_languages_link (book);
CREATE INDEX books_publishers_link_aidx ON books_publishers_link (publisher);
CREATE INDEX books_publishers_link_bidx ON books_publishers_link (book);
CREATE INDEX books_ratings_link_aidx ON books_ratings_link (rating);
CREATE INDEX books_ratings_link_bidx ON books_ratings_link (book);
CREATE INDEX books_series_link_aidx ON books_series_link (series);
CREATE INDEX books_series_link_bidx ON books_series_link (book);
CREATE INDEX books_tags_link_aidx ON books_tags_link (tag);
CREATE INDEX books_tags_link_bidx ON books_tags_link (book);
CREATE INDEX comments_idx ON comments (book);
CREATE INDEX conversion_options_idx_a ON conversion_options (format COLLATE NOCASE);
CREATE INDEX conversion_options_idx_b ON conversion_options (book);
CREATE INDEX custom_columns_idx ON custom_columns (label);
CREATE INDEX data_idx ON data (book);
CREATE INDEX lrp_idx ON last_read_positions (book);
CREATE INDEX formats_idx ON data (format);
CREATE INDEX languages_idx ON languages (lang_code COLLATE NOCASE);
CREATE INDEX publishers_idx ON publishers (name COLLATE NOCASE);
CREATE INDEX series_idx ON series (name COLLATE NOCASE);
CREATE INDEX tags_idx ON tags (name COLLATE NOCASE);
CREATE TRIGGER books_delete_trg
            AFTER DELETE ON books
            BEGIN
                DELETE FROM books_authors_link WHERE book=OLD.id;
                DELETE FROM books_publishers_link WHERE book=OLD.id;
                DELETE FROM books_ratings_link WHERE book=OLD.id;
                DELETE FROM books_series_link WHERE book=OLD.id;
                DELETE FROM books_tags_link WHERE book=OLD.id;
                DELETE FROM books_languages_link WHERE book=OLD.id;
                DELETE FROM data WHERE book=OLD.id;
                DELETE FROM last_read_positions WHERE book=OLD.id;
                DELETE FROM comments WHERE book=OLD.id;
                DELETE FROM conversion_options WHERE book=OLD.id;
                DELETE FROM books_plugin_data WHERE book=OLD.id;
                DELETE FROM identifiers WHERE book=OLD.id;
        END;
CREATE TRIGGER books_insert_trg AFTER INSERT ON books
        BEGIN
            UPDATE books SET sort=title_sort(NEW.title),uuid=uuid4() WHERE id=NEW.id;
        END;
CREATE TRIGGER books_update_trg
            AFTER UPDATE ON books
            BEGIN
            UPDATE books SET sort=title_sort(NEW.title)
                         WHERE id=NEW.id AND OLD.title <> NEW.title;
            END;
CREATE TRIGGER fkc_comments_insert
        BEFORE INSERT ON comments
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_comments_update
        BEFORE UPDATE OF book ON comments
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_data_insert
        BEFORE INSERT ON data
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_data_update
        BEFORE UPDATE OF book ON data
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_lrp_insert
        BEFORE INSERT ON last_read_positions
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_lrp_update
        BEFORE UPDATE OF book ON last_read_positions
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_delete_on_authors
        BEFORE DELETE ON authors
        BEGIN
            SELECT CASE
                WHEN (SELECT COUNT(id) FROM books_authors_link WHERE author=OLD.id) > 0
                THEN RAISE(ABORT, 'Foreign key violation: authors is still referenced')
            END;
        END;
CREATE TRIGGER fkc_delete_on_languages
        BEFORE DELETE ON languages
        BEGIN
            SELECT CASE
                WHEN (SELECT COUNT(id) FROM books_languages_link WHERE lang_code=OLD.id) > 0
                THEN RAISE(ABORT, 'Foreign key violation: language is still referenced')
            END;
        END;
CREATE TRIGGER fkc_delete_on_languages_link
        BEFORE INSERT ON books_languages_link
        BEGIN
          SELECT CASE
              WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: book not in books')
              WHEN (SELECT id from languages WHERE id=NEW.lang_code) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: lang_code not in languages')
          END;
        END;
CREATE TRIGGER fkc_delete_on_publishers
        BEFORE DELETE ON publishers
        BEGIN
            SELECT CASE
                WHEN (SELECT COUNT(id) FROM books_publishers_link WHERE publisher=OLD.id) > 0
                THEN RAISE(ABORT, 'Foreign key violation: publishers is still referenced')
            END;
        END;
CREATE TRIGGER fkc_delete_on_series
        BEFORE DELETE ON series
        BEGIN
            SELECT CASE
                WHEN (SELECT COUNT(id) FROM books_series_link WHERE series=OLD.id) > 0
                THEN RAISE(ABORT, 'Foreign key violation: series is still referenced')
            END;
        END;
CREATE TRIGGER fkc_delete_on_tags
        BEFORE DELETE ON tags
        BEGIN
            SELECT CASE
                WHEN (SELECT COUNT(id) FROM books_tags_link WHERE tag=OLD.id) > 0
                THEN RAISE(ABORT, 'Foreign key violation: tags is still referenced')
            END;
        END;
CREATE TRIGGER fkc_insert_books_authors_link
        BEFORE INSERT ON books_authors_link
        BEGIN
          SELECT CASE
              WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: book not in books')
              WHEN (SELECT id from authors WHERE id=NEW.author) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: author not in authors')
          END;
        END;
CREATE TRIGGER fkc_insert_books_publishers_link
        BEFORE INSERT ON books_publishers_link
        BEGIN
          SELECT CASE
              WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: book not in books')
              WHEN (SELECT id from publishers WHERE id=NEW.publisher) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: publisher not in publishers')
          END;
        END;
CREATE TRIGGER fkc_insert_books_ratings_link
        BEFORE INSERT ON books_ratings_link
        BEGIN
          SELECT CASE
              WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: book not in books')
              WHEN (SELECT id from ratings WHERE id=NEW.rating) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: rating not in ratings')
          END;
        END;
CREATE TRIGGER fkc_insert_books_series_link
        BEFORE INSERT ON books_series_link
        BEGIN
          SELECT CASE
              WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: book not in books')
              WHEN (SELECT id from series WHERE id=NEW.series) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: series not in series')
          END;
        END;
CREATE TRIGGER fkc_insert_books_tags_link
        BEFORE INSERT ON books_tags_link
        BEGIN
          SELECT CASE
              WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: book not in books')
              WHEN (SELECT id from tags WHERE id=NEW.tag) IS NULL
              THEN RAISE(ABORT, 'Foreign key violation: tag not in tags')
          END;
        END;
CREATE TRIGGER fkc_update_books_authors_link_a
        BEFORE UPDATE OF book ON books_authors_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_update_books_authors_link_b
        BEFORE UPDATE OF author ON books_authors_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from authors WHERE id=NEW.author) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: author not in authors')
            END;
        END;
CREATE TRIGGER fkc_update_books_languages_link_a
        BEFORE UPDATE OF book ON books_languages_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_update_books_languages_link_b
        BEFORE UPDATE OF lang_code ON books_languages_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from languages WHERE id=NEW.lang_code) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: lang_code not in languages')
            END;
        END;
CREATE TRIGGER fkc_update_books_publishers_link_a
        BEFORE UPDATE OF book ON books_publishers_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_update_books_publishers_link_b
        BEFORE UPDATE OF publisher ON books_publishers_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from publishers WHERE id=NEW.publisher) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: publisher not in publishers')
            END;
        END;
CREATE TRIGGER fkc_update_books_ratings_link_a
        BEFORE UPDATE OF book ON books_ratings_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_update_books_ratings_link_b
        BEFORE UPDATE OF rating ON books_ratings_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from ratings WHERE id=NEW.rating) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: rating not in ratings')
            END;
        END;
CREATE TRIGGER fkc_update_books_series_link_a
        BEFORE UPDATE OF book ON books_series_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_update_books_series_link_b
        BEFORE UPDATE OF series ON books_series_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from series WHERE id=NEW.series) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: series not in series')
            END;
        END;
CREATE TRIGGER fkc_update_books_tags_link_a
        BEFORE UPDATE OF book ON books_tags_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from books WHERE id=NEW.book) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: book not in books')
            END;
        END;
CREATE TRIGGER fkc_update_books_tags_link_b
        BEFORE UPDATE OF tag ON books_tags_link
        BEGIN
            SELECT CASE
                WHEN (SELECT id from tags WHERE id=NEW.tag) IS NULL
                THEN RAISE(ABORT, 'Foreign key violation: tag not in tags')
            END;
        END;
CREATE TRIGGER series_insert_trg
        AFTER INSERT ON series
        BEGIN
          UPDATE series SET sort=title_sort(NEW.name) WHERE id=NEW.id;
        END;
CREATE TRIGGER series_update_trg
        AFTER UPDATE ON series
        BEGIN
          UPDATE series SET sort=title_sort(NEW.name) WHERE id=NEW.id;
        END;
COMMIT;
"""
