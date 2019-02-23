# Chart-Tools
Parse the XML feeds provided at https://chart.maryland.gov/rss/rssfeeds.asp and return as json/geojson.
Works with the standard library with no additional dependencies.

## Usage Example
    import ChartTools as CT

    # get incidents
    # note no need to init new instance of classes
    my_incidents = CT.Incidents_Feed.get_incidents()

## Classes
### Incidents_Feed
Provides access to the roadway incidents feed.
#### Methods
get_incidents()

### Closures_Feed
Provides access to roadway closures feed.
#### Methods
get_closures() --> returns geojson

### Restrictions_Feed
Provide access to road restrictions feed.
#### Methods
get_restrictions() --> returns json

### Speed_Feed
Provides access to speed sensors feed.
#### Methods
get_sensors() --> returns geojson

### RWIS_Feed
Provide access to roadway weather sensors feed.
#### Methods
get_rwis() --> returns geojson

### DMS_Feed
Provides access to digital message sign feed.
#### Methods
get_msg_board() --> returns geojson

### CCTV_Feed
Provides access to traffic camera feed.
#### Methods
get_cams() --> returns geojson

### Snow_Emergency_Feed
Provides access to snow emergency declarations feed.
#### Methods
get_declarations() --> returns json

