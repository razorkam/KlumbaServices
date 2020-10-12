import logging
from source.HTTPServer import ThreadedHTTPServer
from source.districts_calc.MiscConstants import *
from source.districts_calc.HTTPRequestHandler import RequestHandler
from source.districts_calc.DistrictWorker import DistrictWorker

log = logging.getLogger(__name__)


class DistrictCalc:
    @staticmethod
    def http_serve():
        try:
            deals_update_server = ThreadedHTTPServer((HTTP_SERVER_ADDRESS, HTTP_SERVER_PORT), RequestHandler)

            while True:
                try:
                    deals_update_server.serve_forever()
                except Exception as e:
                    log.error("HTTP server processing exception: ", e)

        except Exception as e:
            log.error("HTTP server init exception: ", e)

    @staticmethod
    def run():
        DistrictWorker.parse_districts_data()
        DistrictCalc.http_serve()
