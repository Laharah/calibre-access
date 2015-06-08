#calibre-access: #
##See who's been using your calibre server ##

Looks for the calibre server_access_log and parses it for downloaded files or search 
requests. 
It then uses the maxmind geolite database to get an approximate geolocation for 
each IP.  
If the maxmind geolite database is not present or out of date, it will be 
downloaded.

###Script Usage###

    calibre-access [LOGFILE|-] [-s]

###Library Usage###

```python
import calibre_access

for record in calibre_access.calibre_downloads():
    print record.location, record.file

for record in calibre_access.calibre_searches():
    print record.location, record.search
```

That's it!
