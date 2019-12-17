import logging
from source.HTTPServer import ThreadedHTTPServer
from logging.handlers import RotatingFileHandler
from source.DistrictWorker import DistrictWorker
from source.HTTPRequestHandler import RequestHandler
from source.MiscConstants import *

LOG_MAX_SIZE = 2 * 1024 * 1024  # 2 mbytes
LOG_LEVEL = logging.INFO


def http_serve():
    try:
        deals_update_server = ThreadedHTTPServer((HTTP_SERVER_ADDRESS, HTTP_SERVER_PORT), RequestHandler)

        while True:
            try:
                deals_update_server.serve_forever()
            except Exception as e:
                logging.error("HTTP server processing exception: ", e)

    except Exception as e:
        logging.error("HTTP server init exception: ", e)


def main():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    log_handler = RotatingFileHandler('app.log', mode='a', maxBytes=LOG_MAX_SIZE,
                                      backupCount=5)
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(LOG_LEVEL)
    logging.getLogger().setLevel(LOG_LEVEL)
    logging.basicConfig(handlers=[log_handler])

    DistrictWorker.parse_districts_data()

    http_serve()


main()
