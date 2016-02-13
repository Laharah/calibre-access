#calibre-access: #
##See who's been using your calibre server ##

Looks for the calibre server_access_log and parses it for downloaded files, search
requests or general webserver logs.
It then uses the maxmind geolite database to get an approximate geolocation for
each IP.  
If the maxmind geolite database is not present or out of date, it will be
downloaded.

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

That's it!
