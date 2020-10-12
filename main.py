import logging
import threading

from source.districts_calc.DistrictsCalc import *

LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s :: %(levelname)s :: %(funcName)s :: (%(lineno)d) :: %(message)s'
SERVICES = []


def main():
    try:
        # journald logging
        logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)



        DistrictCalc.run()
    except Exception as e:
        logging.critical('Main module error: %s', e)


main()
