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
CREATE TABLE books_authors_link ( id INTEGER PRIMARY KEY,
                                          book INTEGER NOT NULL,
                                          author INTEGER NOT NULL,
                                          UNIQUE(book, author)
                                        );
INSERT INTO "books_authors_link" VALUES(1,1,1);
INSERT INTO "books_authors_link" VALUES(2,2,1);
INSERT INTO "books_authors_link" VALUES(3,3,2);
INSERT INTO "books_authors_link" VALUES(4,4,2);
CREATE TABLE books_languages_link ( id INTEGER PRIMARY KEY,
                                            book INTEGER NOT NULL,
                                            lang_code INTEGER NOT NULL,
                                            item_order INTEGER NOT NULL DEFAULT 0,
                                            UNIQUE(book, lang_code)
        );
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
CREATE TABLE books_ratings_link ( id INTEGER PRIMARY KEY,
                                          book INTEGER NOT NULL,
                                          rating INTEGER NOT NULL,
                                          UNIQUE(book, rating)
                                        );
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
CREATE TABLE comments ( id INTEGER PRIMARY KEY,
                              book INTEGER NOT NULL,
                              text TEXT NOT NULL COLLATE NOCASE,
                              UNIQUE(book)
                            );
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
CREATE TABLE languages    ( id        INTEGER PRIMARY KEY,
                                    lang_code TEXT NOT NULL COLLATE NOCASE,
                                    UNIQUE(lang_code)
        );
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
INSERT INTO "preferences" VALUES(1,'bools_are_tristate','true');
INSERT INTO "preferences" VALUES(2,'user_categories','{}');
INSERT INTO "preferences" VALUES(3,'saved_searches','{}');
INSERT INTO "preferences" VALUES(4,'grouped_search_terms','{}');
INSERT INTO "preferences" VALUES(5,'tag_browser_hidden_categories','[]');
INSERT INTO "preferences" VALUES(6,'field_metadata','{
  "au_map": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {
      "cache_to_list": ",", 
      "list_to_ui": null, 
      "ui_to_list": null
    }, 
    "kind": "field", 
    "label": "au_map", 
    "name": null, 
    "rec_index": 18, 
    "search_terms": [], 
    "table": null
  }, 
  "author_sort": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "author_sort", 
    "name": "Author sort", 
    "rec_index": 12, 
    "search_terms": [
      "author_sort"
    ], 
    "table": null
  }, 
  "authors": {
    "category_sort": "sort", 
    "column": "name", 
    "datatype": "text", 
    "display": {}, 
    "is_category": true, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {
      "cache_to_list": ",", 
      "list_to_ui": " & ", 
      "ui_to_list": "&"
    }, 
    "kind": "field", 
    "label": "authors", 
    "link_column": "author", 
    "name": "Authors", 
    "rec_index": 2, 
    "search_terms": [
      "authors", 
      "author"
    ], 
    "table": "authors"
  }, 
  "comments": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "comments", 
    "name": "Comments", 
    "rec_index": 7, 
    "search_terms": [
      "comments", 
      "comment"
    ], 
    "table": null
  }, 
  "cover": {
    "column": null, 
    "datatype": "int", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "cover", 
    "name": "Cover", 
    "rec_index": 17, 
    "search_terms": [
      "cover"
    ], 
    "table": null
  }, 
  "formats": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": true, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {
      "cache_to_list": ",", 
      "list_to_ui": ", ", 
      "ui_to_list": ","
    }, 
    "kind": "field", 
    "label": "formats", 
    "name": "Formats", 
    "rec_index": 13, 
    "search_terms": [
      "formats", 
      "format"
    ], 
    "table": null
  }, 
  "id": {
    "column": null, 
    "datatype": "int", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "id", 
    "name": null, 
    "rec_index": 0, 
    "search_terms": [
      "id"
    ], 
    "table": null
  }, 
  "identifiers": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": true, 
    "is_csp": true, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {
      "cache_to_list": ",", 
      "list_to_ui": ", ", 
      "ui_to_list": ","
    }, 
    "kind": "field", 
    "label": "identifiers", 
    "name": "Identifiers", 
    "rec_index": 20, 
    "search_terms": [
      "identifiers", 
      "identifier", 
      "isbn"
    ], 
    "table": null
  }, 
  "languages": {
    "category_sort": "lang_code", 
    "column": "lang_code", 
    "datatype": "text", 
    "display": {}, 
    "is_category": true, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {
      "cache_to_list": ",", 
      "list_to_ui": ", ", 
      "ui_to_list": ","
    }, 
    "kind": "field", 
    "label": "languages", 
    "link_column": "lang_code", 
    "name": "Languages", 
    "rec_index": 21, 
    "search_terms": [
      "languages", 
      "language"
    ], 
    "table": "languages"
  }, 
  "last_modified": {
    "column": null, 
    "datatype": "datetime", 
    "display": {
      "date_format": "dd MMM yyyy"
    }, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "last_modified", 
    "name": "Modified", 
    "rec_index": 19, 
    "search_terms": [
      "last_modified"
    ], 
    "table": null
  }, 
  "marked": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "marked", 
    "name": null, 
    "rec_index": 23, 
    "search_terms": [
      "marked"
    ], 
    "table": null
  }, 
  "news": {
    "category_sort": "name", 
    "column": "name", 
    "datatype": null, 
    "display": {}, 
    "is_category": true, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "category", 
    "label": "news", 
    "name": "News", 
    "search_terms": [], 
    "table": "news"
  }, 
  "ondevice": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "ondevice", 
    "name": "On device", 
    "rec_index": 22, 
    "search_terms": [
      "ondevice"
    ], 
    "table": null
  }, 
  "path": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "path", 
    "name": "Path", 
    "rec_index": 14, 
    "search_terms": [], 
    "table": null
  }, 
  "pubdate": {
    "column": null, 
    "datatype": "datetime", 
    "display": {
      "date_format": "MMM yyyy"
    }, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "pubdate", 
    "name": "Published", 
    "rec_index": 15, 
    "search_terms": [
      "pubdate"
    ], 
    "table": null
  }, 
  "publisher": {
    "category_sort": "name", 
    "column": "name", 
    "datatype": "text", 
    "display": {}, 
    "is_category": true, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "publisher", 
    "link_column": "publisher", 
    "name": "Publisher", 
    "rec_index": 9, 
    "search_terms": [
      "publisher"
    ], 
    "table": "publishers"
  }, 
  "rating": {
    "category_sort": "rating", 
    "column": "rating", 
    "datatype": "rating", 
    "display": {}, 
    "is_category": true, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "rating", 
    "link_column": "rating", 
    "name": "Rating", 
    "rec_index": 5, 
    "search_terms": [
      "rating"
    ], 
    "table": "ratings"
  }, 
  "series": {
    "category_sort": "(title_sort(name))", 
    "column": "name", 
    "datatype": "series", 
    "display": {}, 
    "is_category": true, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "series", 
    "link_column": "series", 
    "name": "Series", 
    "rec_index": 8, 
    "search_terms": [
      "series"
    ], 
    "table": "series"
  }, 
  "series_index": {
    "column": null, 
    "datatype": "float", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "series_index", 
    "name": null, 
    "rec_index": 10, 
    "search_terms": [
      "series_index"
    ], 
    "table": null
  }, 
  "series_sort": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "series_sort", 
    "name": "Series sort", 
    "rec_index": 24, 
    "search_terms": [
      "series_sort"
    ], 
    "table": null
  }, 
  "size": {
    "column": null, 
    "datatype": "float", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "size", 
    "name": "Size", 
    "rec_index": 4, 
    "search_terms": [
      "size"
    ], 
    "table": null
  }, 
  "sort": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "sort", 
    "name": "Title sort", 
    "rec_index": 11, 
    "search_terms": [
      "title_sort"
    ], 
    "table": null
  }, 
  "tags": {
    "category_sort": "name", 
    "column": "name", 
    "datatype": "text", 
    "display": {}, 
    "is_category": true, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {
      "cache_to_list": ",", 
      "list_to_ui": ", ", 
      "ui_to_list": ","
    }, 
    "kind": "field", 
    "label": "tags", 
    "link_column": "tag", 
    "name": "Tags", 
    "rec_index": 6, 
    "search_terms": [
      "tags", 
      "tag"
    ], 
    "table": "tags"
  }, 
  "timestamp": {
    "column": null, 
    "datatype": "datetime", 
    "display": {
      "date_format": "dd MMM yyyy"
    }, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "timestamp", 
    "name": "Date", 
    "rec_index": 3, 
    "search_terms": [
      "date"
    ], 
    "table": null
  }, 
  "title": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "title", 
    "name": "Title", 
    "rec_index": 1, 
    "search_terms": [
      "title"
    ], 
    "table": null
  }, 
  "uuid": {
    "column": null, 
    "datatype": "text", 
    "display": {}, 
    "is_category": false, 
    "is_csp": false, 
    "is_custom": false, 
    "is_editable": true, 
    "is_multiple": {}, 
    "kind": "field", 
    "label": "uuid", 
    "name": null, 
    "rec_index": 16, 
    "search_terms": [
      "uuid"
    ], 
    "table": null
  }
}');
INSERT INTO "preferences" VALUES(7,'library_view books view state','{
  "column_alignment": {
    "pubdate": "center", 
    "size": "center", 
    "timestamp": "center"
  }, 
  "column_positions": {
    "authors": 2, 
    "languages": 11, 
    "last_modified": 10, 
    "ondevice": 0, 
    "pubdate": 9, 
    "publisher": 8, 
    "rating": 5, 
    "series": 7, 
    "size": 4, 
    "tags": 6, 
    "timestamp": 3, 
    "title": 1
  }, 
  "column_sizes": {
    "authors": 90, 
    "languages": 0, 
    "last_modified": 0, 
    "pubdate": 92, 
    "publisher": 89, 
    "rating": 70, 
    "series": 118, 
    "size": 90, 
    "tags": 59, 
    "timestamp": 70, 
    "title": 152
  }, 
  "hidden_columns": [
    "last_modified", 
    "languages"
  ], 
  "languages_injected": true, 
  "last_modified_injected": true, 
  "sort_history": [
    [
      "timestamp", 
      false
    ]
  ]
}');
CREATE TABLE publishers ( id   INTEGER PRIMARY KEY,
                                  name TEXT NOT NULL COLLATE NOCASE,
                                  sort TEXT COLLATE NOCASE,
                                  UNIQUE(name)
                             );
CREATE TABLE ratings ( id   INTEGER PRIMARY KEY,
                               rating INTEGER CHECK(rating > -1 AND rating < 11),
                               UNIQUE (rating)
                             );
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
INSERT INTO "sqlite_sequence" VALUES('books',4);
CREATE VIEW meta AS
        SELECT id, title,
               (SELECT sortconcat(bal.id, name) FROM books_authors_link AS bal JOIN authors ON(author = authors.id) WHERE book = books.id) authors,
               (SELECT name FROM publishers WHERE publishers.id IN (SELECT publisher from books_publishers_link WHERE book=books.id)) publisher,
               (SELECT rating FROM ratings WHERE ratings.id IN (SELECT rating from books_ratings_link WHERE book=books.id)) rating,
               timestamp,
               (SELECT MAX(uncompressed_size) FROM data WHERE book=books.id) size,
               (SELECT concat(name) FROM tags WHERE tags.id IN (SELECT tag from books_tags_link WHERE book=books.id)) tags,
               (SELECT text FROM comments WHERE book=books.id) comments,
               (SELECT name FROM series WHERE series.id IN (SELECT series FROM books_series_link WHERE book=books.id)) series,
               series_index,
               sort,
               author_sort,
               (SELECT concat(format) FROM data WHERE data.book=books.id) formats,
               isbn,
               path,
               lccn,
               pubdate,
               flags,
               uuid
        FROM books;
CREATE VIEW tag_browser_authors AS SELECT
                    id,
                    name,
                    (SELECT COUNT(id) FROM books_authors_link WHERE author=authors.id) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_authors_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.author=authors.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0) avg_rating,
                     sort AS sort
                FROM authors;
CREATE VIEW tag_browser_filtered_authors AS SELECT
                    id,
                    name,
                    (SELECT COUNT(books_authors_link.id) FROM books_authors_link WHERE
                        author=authors.id AND books_list_filter(book)) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_authors_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.author=authors.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0 AND
                     books_list_filter(bl.book)) avg_rating,
                     sort AS sort
                FROM authors;
CREATE VIEW tag_browser_filtered_publishers AS SELECT
                    id,
                    name,
                    (SELECT COUNT(books_publishers_link.id) FROM books_publishers_link WHERE
                        publisher=publishers.id AND books_list_filter(book)) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_publishers_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.publisher=publishers.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0 AND
                     books_list_filter(bl.book)) avg_rating,
                     name AS sort
                FROM publishers;
CREATE VIEW tag_browser_filtered_ratings AS SELECT
                    id,
                    rating,
                    (SELECT COUNT(books_ratings_link.id) FROM books_ratings_link WHERE
                        rating=ratings.id AND books_list_filter(book)) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_ratings_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.rating=ratings.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0 AND
                     books_list_filter(bl.book)) avg_rating,
                     rating AS sort
                FROM ratings;
CREATE VIEW tag_browser_filtered_series AS SELECT
                    id,
                    name,
                    (SELECT COUNT(books_series_link.id) FROM books_series_link WHERE
                        series=series.id AND books_list_filter(book)) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_series_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.series=series.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0 AND
                     books_list_filter(bl.book)) avg_rating,
                     (title_sort(name)) AS sort
                FROM series;
CREATE VIEW tag_browser_filtered_tags AS SELECT
                    id,
                    name,
                    (SELECT COUNT(books_tags_link.id) FROM books_tags_link WHERE
                        tag=tags.id AND books_list_filter(book)) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_tags_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.tag=tags.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0 AND
                     books_list_filter(bl.book)) avg_rating,
                     name AS sort
                FROM tags;
CREATE VIEW tag_browser_publishers AS SELECT
                    id,
                    name,
                    (SELECT COUNT(id) FROM books_publishers_link WHERE publisher=publishers.id) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_publishers_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.publisher=publishers.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0) avg_rating,
                     name AS sort
                FROM publishers;
CREATE VIEW tag_browser_ratings AS SELECT
                    id,
                    rating,
                    (SELECT COUNT(id) FROM books_ratings_link WHERE rating=ratings.id) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_ratings_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.rating=ratings.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0) avg_rating,
                     rating AS sort
                FROM ratings;
CREATE VIEW tag_browser_series AS SELECT
                    id,
                    name,
                    (SELECT COUNT(id) FROM books_series_link WHERE series=series.id) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_series_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.series=series.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0) avg_rating,
                     (title_sort(name)) AS sort
                FROM series;
CREATE VIEW tag_browser_tags AS SELECT
                    id,
                    name,
                    (SELECT COUNT(id) FROM books_tags_link WHERE tag=tags.id) count,
                    (SELECT AVG(ratings.rating)
                     FROM books_tags_link AS tl, books_ratings_link AS bl, ratings
                     WHERE tl.tag=tags.id AND bl.book=tl.book AND
                     ratings.id = bl.rating AND ratings.rating <> 0) avg_rating,
                     name AS sort
                FROM tags;
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
