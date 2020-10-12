import json
import re
from shapely.geometry import Polygon
import logging
from source.districts_calc import MiscConstants
from source.districts_calc.District import District
from source.districts_calc.DCBitrixWorker import DCBitrixWorker

log = logging.getLogger(__name__)
BITRIX_ADDRESS_PATTERN = re.compile('(.+)\\|(\\d+\\.\\d+);(\\d+\\.\\d+)') #address|lat;lon

class DistrictWorker:
    districts_polygons = []
    districts_field_data = {}

    @staticmethod
    def parse_districts_data():

        try:
            with open(MiscConstants.DISTRICTS_FILENAME) as f:
                DistrictWorker.districts_polygons = []
                data = json.load(f)

                for feature in data['features']:
                    name = feature['properties']['name'].lower()
                    geometry = feature['geometry']
                    geometry_type = geometry['type']
                    polygon_data = []

                    if geometry_type == 'Polygon':
                        polygon_data = geometry['coordinates'][0]
                    # handling multipolygons of 1 polygon only for now
                    elif geometry_type == 'MultiPolygon':
                        polygon_data = geometry['coordinates'][0][0]
                    else:
                        raise TypeError("Unknown geometry type: {}".format(geometry_type))

                    polygon = Polygon(polygon_data)
                    district = District(polygon, name)

                    DistrictWorker.districts_polygons.append(district)

            field_data = DCBitrixWorker.get_district_field_data()

            if not field_data:
                raise Exception('Bitrix district fields cannot be obtained')

            for obj in field_data['LIST']:
                code = obj['ID']
                name = obj['VALUE'].lower()
                DistrictWorker.districts_field_data[name] = code

        except Exception as e:
            log.error("Parsing districts geodata error %s", e)

    @staticmethod
    def get_district_name(address_point):
        for d in DistrictWorker.districts_polygons:
            name = d.contains(address_point)

            if name:
                return name

        return None


    @staticmethod
    def get_location(address_str):
        location = BITRIX_ADDRESS_PATTERN.search(address_str)

        if location:
            lat = location.group(2)
            lon = location.group(3)

            return lat, lon
        else:
            log.error('Location cannot be parsed with address regex {}'.format(address_str))
            return None, None


    @staticmethod
    def get_district_code(name):
        if name in DistrictWorker.districts_field_data:
            return DistrictWorker.districts_field_data[name]
        else:
            return None