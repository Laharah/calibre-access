[![Build Status](https://travis-ci.org/Laharah/calibre-access.svg?branch=master)](https://travis-ci.org/Laharah/calibre-access)
#calibre-access: #
##See who's been using your calibre server ##


Looks for the calibre server_access_log and parses it for downloaded files, search
requests or general webserver logs.
It then uses the maxmind geolite database to get an approximate geolocation for
each IP.  
If the maxmind geolite database is not present or out of date, it will be
downloaded.

supports python 2.7, 3.3, 3.4, and 3.5; OS-X, Linux, Windows

###Script Usage###

    calibre-access [options] [LOGFILE|-]

        -d, --downloads   Parse download records (defaut record if none specified)
        -s, --searches    Parse search records
        -b, --bare        do not show total records or total unique ip's
        --time-filter s   number of seconds to filter out non-unique records by.
                          this filters rapid reloads/downloads. defaults to 10

###Library Usage###

```python
import calibre_access

for record in calibre_access.calibre_downloads():
    print record['location'], record['file']

for record in calibre_access.calibre_searches():
    print record['location'], record['query']
```

###Installation###

you can either clone the repository then test/install with:
```bash
python setup.py test
python setup.py install
```

or you can install directly with pip:

    pip install git+https://github.com/Laharah/calibre-access.git
