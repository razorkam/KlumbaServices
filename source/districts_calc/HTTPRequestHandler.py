from http.server import BaseHTTPRequestHandler
from urllib import parse
import logging
import json
from shapely.geometry import Point

from source.districts_calc.DCBitrixWorker import *
from source.districts_calc.DistrictWorker import DistrictWorker
from source.districts_calc.BitrixFieldMappings import *
from source import creds

logger = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    def send_json(self, source_dict):
        self.send_response(200)
        # WARNING: CORS restrictions disabled
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(source_dict).encode())

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        BaseHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        try:
            logger.info("New GET request accepted!")
            query = parse.urlparse(self.path).query
            query_components = parse.parse_qs(query, keep_blank_values=True)
            logger.info("Accepted query components: %s", query_components)

            service = query_components[WEBHOOK_SERVICE_ALIAS][0]

            if service == BITRIX_SERVICE_COMPUTE_DISTRICT:
                lat = query_components[WEBHOOK_LAT_ALIAS][0]
                lon = query_components[WEBHOOK_LON_ALIAS][0]

                if not lat or not lon:
                    self.send_error(400, "No latitude/longtitude for district computing")
                    raise Exception('No latitude/longtitude for district computing')

                # DistrictWorker stores polygon's point in (lon,lat) format
                point = Point(float(lon), float(lat))
                district_name = DistrictWorker.get_district_name(point)

                if district_name:
                    district_code = DistrictWorker.get_district_code(district_name)
                    if district_code:
                        self.send_json({'district_id': district_code})
                    else:
                        self.send_error(500, 'District code was not found by name {}'.format(district_name))
                        raise Exception('District code was not found by name {}'.format(district_name))

                else:
                    self.send_error(500, 'District name was not computed successfully for location: {};{}'
                                    .format(lat, lon))
                    raise Exception('District name was not computed successfully for location: {};{}'
                                    .format(lat, lon))
            else:
                self.send_error(400, 'Unknown service type: {}'.format(service))
                raise TypeError('Unknown service type: {}'.format(service))

        except Exception as e:
            self.send_error(400, 'Request parameters error')
            logger.error('HTTP request handling error: %s', e)

