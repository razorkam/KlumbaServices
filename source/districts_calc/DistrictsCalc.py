import logging
import ssl
import time

from source.HTTPServer import ThreadedHTTPServer
from source.districts_calc.MiscConstants import *
from source.districts_calc.HTTPRequestHandler import RequestHandler
from source.districts_calc.DistrictWorker import DistrictWorker
from source.RunnableService import RunnableService

log = logging.getLogger(__name__)


class DistrictCalc(RunnableService):
    GLOBAL_ERROR_TIMEOUT = 60

    @staticmethod
    def http_serve():
        try:
            deals_update_server = ThreadedHTTPServer((HTTP_SERVER_ADDRESS, HTTP_SERVER_PORT), RequestHandler)
            deals_update_server.socket = ssl.wrap_socket(deals_update_server.socket,
                                                         keyfile=CERTKEY_PATH, certfile=CERT_PATH,
                                                         server_side=True)

            while True:
                try:
                    deals_update_server.serve_forever()
                except Exception as e:
                    log.error("HTTP server processing exception: ", e)

        except Exception as e:
            log.error("HTTP server init exception: ", e)
            time.sleep(DistrictCalc.GLOBAL_ERROR_TIMEOUT)

    @staticmethod
    def run():
        while True:
            try:
                DistrictWorker.parse_districts_data()
                DistrictCalc.http_serve()
            except Exception as e:
                log.critical('Error running DistrictsCalc service: %s', e)
                time.sleep(DistrictCalc.GLOBAL_ERROR_TIMEOUT)
