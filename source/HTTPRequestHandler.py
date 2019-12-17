from http.server import BaseHTTPRequestHandler
from urllib import parse
import logging
from shapely.geometry import Point

from .BitrixFieldsAliases import *
from . import BitrixFieldMappings
from .BitrixWorker import BitrixWorker
from .DistrictWorker import DistrictWorker
from .BitrixFieldMappings import *
from . import creds


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            logging.info("New POST request accepted!")
            query = parse.urlparse(self.path).query
            query_components = parse.parse_qs(query, keep_blank_values=True)
            logging.info("Accepted query components: %s", query_components)

            if WEBHOOK_SECRET_ALIAS in query_components \
                    and query_components[WEBHOOK_SECRET_ALIAS][0] == creds.BITRIX_WEBHOOK_SECRET:

                service = query_components[WEBHOOK_SERVICE_ALIAS][0]

                if service == BITRIX_SERVICE_COMPUTE_DISTRICT:
                    deal_id = query_components[WEBHOOK_DEAL_ID_ALIAS][0]
                    address = query_components[WEBHOOK_ADDRESS_ALIAS][0]

                    lat, lon = DistrictWorker.get_location(address)

                    if not lat or not lon:
                        return

                    # DistrictWorker stores polygon's point in (lon,lat) format
                    point = Point(float(lon), float(lat))
                    district_name = DistrictWorker.get_district_name(point)

                    if district_name:
                        district_code = DistrictWorker.get_district_code(district_name)
                        if district_code:
                            result = BitrixWorker.set_district(deal_id, district_code)

                            if result:
                                logging.info("Deal id {} district was updated successfully!".format(deal_id))
                            else:
                                logging.info("Deal id {} district was not updated: bitrix updating error"
                                             .format(deal_id))
                        else:
                            raise Exception('District code was not found by name {}'.format(district_name))

                    else:
                        raise Exception('District name was not computed successfully for address: {}'.format(address))

                else:
                    raise TypeError('Unknown service type: {}'.format(service))

            else:
                raise Exception('Secret hasnt passed or incorrect')

        except Exception as e:
            logging.error('HTTP request handling error: %s', e)

