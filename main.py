import logging
import threading

from source.districts_calc.DistrictsCalc import *
from source.retail_feedback.RetailFeedback import *

LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s :: %(levelname)s :: %(funcName)s :: (%(lineno)d) :: %(message)s'
SERVICES = [DistrictCalc, RetailFeedback]


def main():
    try:
        # journald logging
        logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

        # run 1: in separate threads
        for s in SERVICES[1:]:
            t = threading.Thread(target=s.run)
            t.start()


        SERVICES[0].run()
    except Exception as e:
        logging.critical('Main module error: %s', e)


main()
