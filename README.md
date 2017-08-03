[![Build Status](https://travis-ci.org/Laharah/calibre-access.svg?branch=master)](https://travis-ci.org/Laharah/calibre-access)
# calibre-access: #
## See who's been using your calibre server ##


Looks for the calibre server_access_log and parses it for downloaded files, search
requests or general webserver logs.
It then uses the maxmind geolite database to get an approximate geolocation for
each IP.  
If the maxmind geolite database is not present or out of date, it will be
downloaded.

supports python 2.7, 3.3, 3.4, and 3.5; OS-X, Linux, Windows

### Script Usage ###

    calibre-access [options] [LOGFILE|-]

        -d, --downloads   Parse download records (defaut record if none specified)
        -s, --searches    Parse search records
        -b, --bare        do not show total records or total unique ip's
        --time-filter s   number of seconds to filter out non-unique records by.
                          this filters rapid reloads/downloads. defaults to 10

### Library Usage ###

```python
import calibre_access

for record in calibre_access.calibre_downloads():
    print record['datetime'], record['file']

for record in calibre_access.calibre_searches():
    print record['datetime'], record['query']
```

calibre-access uses a generator pipeline strategy to process log information,
you can find useful data processing functions in the `calibre_access.utilities` module
and two pre-written filtering coroutines in the `calibre_access.calibre_access` module.

By combining these pre-written data processors and writing your own, you can easily compose your own data pipline for your calibre data. For example, you could find the 3 most
common filetypes downloaded from your server in the last year like so:
```python
from collections import Counter
from datetime import datetime, timedelta
from calibre_access import calibre_downloads

def last_year(records):  # filters for records in the last year
    year = timedelta(365)
    for record in records:
        if datetime.now() - record['datetime'] < year:
            yield record

def extension(records):
    for record in records:
        yield record['file'].split('.')[-1]

# set up our pipeline
records = calibre_downloads()
new_records = last_year(records)
file_types = extension(new_records)

# feed our pipeline into some consumer or for loop
print Counter(file_types).most_common(3)

```
The output should look something like this:

`>>> [(u'epub', 130), (u'mobi', 62), (u'azw3', 8)]`

See the [main function in the calibre_access](https://github.com/Laharah/calibre-access/blob/master/calibre_access/calibre_access.py#L257-L266)
module to see the pipeline that powers the command line invocation.


### Installation ###

you can either clone the repository then test/install with:
```bash
python setup.py test
python setup.py install
```

or you can install directly with pip:

    pip install git+https://github.com/Laharah/calibre-access.git
