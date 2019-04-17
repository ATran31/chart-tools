import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


class _CHART(object):
    '''
    Private class to hold common methods accross various child classes that represent CHART data feeds. Should not be called externally.
    '''
    @staticmethod
    def get_geojson(url):
        '''
        Parse XML geographic objects returned by the CHART service into feature collection dict or None if no data is found.
        '''
        feature_collection = {'type': 'FeatureCollection', 'featureCount': 0, 'features': []}

        # submit request for data
        request = urllib.request.urlopen(url)
        response = request.read()

        # parse xml response
        records = ET.fromstring(response)
        for record in records:
            feature = {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [0, 0]}}

            for attribute in record:
                feature['properties'][attribute.tag] = attribute.text

            # assign coordinates, order should be [lon, lat]
            feature['geometry']['coordinates'][0] = feature['properties']['longitude']
            feature['geometry']['coordinates'][1] = feature['properties']['latitude']

            feature_collection['features'].append(feature)

            # increase feature collection feature count by 1
            feature_collection['featureCount'] += 1

        if feature_collection['featureCount'] > 0:
            return feature_collection
        return None


class Incidents_Feed(_CHART):
    '''
    Access incident XML feed from CHART.
    '''
    service_url = 'https://chart.maryland.gov/rss/ProduceRSS.aspx?Type=TIandRCXML&filter=TI'

    @staticmethod
    def get_geojson(url):
        '''
        Overrides super implemenation of get_geojson() to handle additional nesting of XML attributes.
        '''
        feature_collection = {'type': 'FeatureCollection', 'featureCount': 0, 'features': []}

        # submit request for data
        request = urllib.request.urlopen(url)
        response = request.read()

        # parse xml response
        incidents = ET.fromstring(response)
        for incident in incidents:
            feature = {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [0, 0]}}

            for attribute in incident:
                if attribute.tag != 'lanes':
                    feature['properties'][attribute.tag] = attribute.text
                else:
                    # create list to hold lane info
                    lanes = []
                    for lane in attribute:
                        # each lane will be a dict with k-v pair of lane attributes
                        lane_obj = {}
                        for field in lane:
                            lane_obj[field.tag] = field.text
                        lanes.append(lane_obj)
                    # feature property 'lanes' will be assigned a list of lane dicts
                    feature['properties'][attribute.tag] = lanes

            # assign coordinates, order should be [lon, lat]
            feature['geometry']['coordinates'][0] = feature['properties']['longitude']
            feature['geometry']['coordinates'][1] = feature['properties']['latitude']

            feature_collection['features'].append(feature)

            # increase feature collection feature count by 1
            feature_collection['featureCount'] += 1

        if feature_collection['featureCount'] > 0:
            return feature_collection
        return None

    @classmethod
    def get_incidents(cls):
        '''
        Returns a geojson feature collection of incidents or None if no data is found.
        '''
        cls.get_geojson(cls.service_url)


class Closures_Feed(_CHART):
    '''
    Access road closures XML feed from CHART.
    '''
    service_url = 'https://chart.maryland.gov/rss/ProduceRSS.aspx?Type=TIandRCXML&filter=RC'

    @staticmethod
    def get_geojson(url):
        '''
        Overrides super implemenation of get_geojson() to handle additional nesting of XML attributes.
        '''
        feature_collection = {'type': 'FeatureCollection', 'featureCount': 0, 'features': []}

        # submit request for data
        request = urllib.request.urlopen(url)
        response = request.read()

        # parse xml response
        closures = ET.fromstring(response)
        for closure_types in closures:
            for closure in closure_types:
                feature = {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [0, 0]}}
                for attribute in closure:
                    if attribute.tag != 'lanes':
                        feature['properties'][attribute.tag] = attribute.text
                    else:
                        # create list to hold lane info
                        lanes = []
                        for lane in attribute:
                            # each lane will be a dict with k-v pair of lane attributes
                            lane_obj = {}
                            for field in lane:
                                lane_obj[field.tag] = field.text
                            lanes.append(lane_obj)
                        # feature property 'lanes' will be assigned a list of lane dicts
                        feature['properties'][attribute.tag] = lanes

            # assign coordinates, order should be [lon, lat]
            feature['geometry']['coordinates'][0] = feature['properties']['longitude']
            feature['geometry']['coordinates'][1] = feature['properties']['latitude']

            feature_collection['features'].append(feature)

            # increase feature collection feature count by 1
            feature_collection['featureCount'] += 1

        if feature_collection['featureCount'] > 0:
            return feature_collection
        return None

    @classmethod
    def get_closures(cls):
        '''
        Returns a geojson feature collection of road closures or None if no data is found.
        '''
        cls.get_geojson(cls.service_url)


class Restrictions_Feed(object):
    '''
    Access route restrictions XML feed from CHART.
    '''
    service_url = 'https://chart.maryland.gov/rss/ProduceRSS.aspx?Type=RouteRestrictionsXML&filter=ALL'

    @classmethod
    def get_restrictions(cls, route_type=None):
        '''
        Lists snow route restrictions throughout the state.
        Returns a JSON or None if no data found.

        Keyword Argument:
        route_type (optional) -- The type of route to filter results by. Valid values are 'Interstate Highways', 'U.S. Highways', 'Maryland State Highways', or 'Local Area Restrictions'.
        '''
        # container to hold results
        restrictions = {'restrictions': []}

        # submit request for data
        if route_type is None:
            request = urllib.request.urlopen(cls.service_url)
        else:
            url = cls.service_url + '&' + urllib.parse.urlencode({'filter': route_type})
            request = urllib.request.urlopen(url)
        response = request.read()

        # parse xml response
        restrictions = ET.fromstring(response)
        for restriction in restrictions:
            properties = {}
            for rule in restriction:
                properties[rule.tag] = rule.text
            restrictions['restrictions'].append(properties)

        if len(restrictions['restrictions']) > 0:
            return restrictions
        return None


class Speed_Feed(_CHART):
    '''
    Access speed sensor XML feed from CHART.
    '''
    service_url = 'https://chart.maryland.gov/rss/ProduceRSS.aspx?Type=TravelSpeedsXML'

    @classmethod
    def get_sensors(cls, route=None):
        '''
        Returns a geojson feature collection of speed sensors or None if no data is found.

        Keyword argument:
        route (optional) -- The route to filter results by e.g. 'I-95'. Valid values includes all interstates, US-50, MD-32, and MD-140.
        '''
        if route is None:
            return cls.get_geojson(cls.service_url)
        else:
            url = cls.service_url + '&' + urllib.parse.urlencode({'filter': route})
            return cls.get_geojson(url)


class RWIS_Feed(_CHART):
    '''
    Access to RWIS XML feed from CHART.
    '''
    service_url = 'https://chart.maryland.gov/rss/ProduceRss.aspx?Type=WeatherStationXML'

    @classmethod
    def get_sensors(cls, station_name=None):
        '''
        Returns a geojson feature collection of RWIS sensors or None if no data is found.

        Keyword Argument:
        station_name (optional) -- The name of the station to filter by e.g. 'IS 270 N, North of MD 80'
        '''
        if station_name is None:
            return cls.get_geojson(cls.service_url)
        else:
            url = cls.service_url + '&' + urllib.parse.urlencode({'filter': station_name})
            return cls.get_geojson(url)


class DMS_Feed(_CHART):
    '''
    Access DMS XML from CHART.
    '''
    service_url = 'https://chart.maryland.gov/rss/ProduceRss.aspx?Type=DMSXML'

    @classmethod
    def get_msg_boards(cls):
        '''
        Returns a geojson of traffic cctv or None if no data is found.
        '''
        return cls.get_geojson(cls.service_url)


class CCTV_Feed(_CHART):
    '''
    Access to traffic camera XML feed from CHART.
    '''
    service_url = 'https://chart.maryland.gov/rss/ProduceRss.aspx?Type=VIDEOXML'

    @classmethod
    def get_cams(cls):
        '''
        Returns a geojson of traffic cctv or None if no data is found.
        '''
        return cls.get_geojson(cls.service_url)


class Snow_Emergency_Feed(object):
    '''
    Access snow emergency XML feed from CHART.
    '''
    service_url = 'https://chart.maryland.gov/rss/ProduceRss.aspx?Type=SNEMXML'

    @classmethod
    def get_declarations(cls):
        '''
        Lists snow emergency delcarations throughout the state.
        Returns a JSON or None if no data found.
        '''
        # container to hold results
        declarations = {'declarations': []}

        # submit request for data
        request = urllib.request.urlopen(cls.service_url)
        response = request.read()

        # parse xml response
        events = ET.fromstring(response)
        for event in events:
            event = {}
            for declaration in event:
                event[declaration.tag] = declaration.text
            declarations['declarations'].append(event)

        if len(declarations['declarations']) > 0:
            return declarations
        return None
