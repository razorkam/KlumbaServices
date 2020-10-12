import requests
from . import creds
import logging

log = logging.getLogger(__name__)


class BitrixWorker:
    SESSION = requests.session()
    REQUESTS_TIMEOUT = 10
    REQUESTS_MAX_ATTEMPTS = 3

    @staticmethod
    def _send_request(method, params=None, custom_error_text=''):
        if params is None:
            params = {}

        for a in range(BitrixWorker.REQUESTS_MAX_ATTEMPTS):
            try:
                response = BitrixWorker.SESSION.post(url=creds.BITRIX_API_URL + method,
                                                     json=params, timeout=BitrixWorker.REQUESTS_TIMEOUT)

                if response and response.ok:
                    json = response.json()

                    if 'result' in json:
                        return json['result']
                    else:
                        error = 'Bitrix bad response %s : Attempt: %s, Called: %s : Request params: %s' \
                                % (a, json, custom_error_text, params)
                        log.error(error)
                else:
                    error = 'Bitrix response failed - %s : Attempt: %s,  Called: %s : Request params: %s' \
                            % (a, response.text, custom_error_text, params)
                    log.error(error)

            except Exception as e:
                error = 'Sending Bitrix api request %s' % e
                log.error(error)

        return None
