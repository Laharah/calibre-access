#calibre-access: #
##See who's been using your calibre server ##

Looks for the calibre server_access_log and parses it for downloaded files. 
It then uses the maxmind geolite database to get an approximate geolocation for 
each IP.  
If the maxmind geolite database is not present or out of date, it will be 
downloaded.

###Script Usage###

    calibre-access [LOGFILE|-]

###Library Usage###

```python
from calibre_access import calibre_downloads

for record in calibre_downloads():
    print record.location, record.file
```

That's it!
