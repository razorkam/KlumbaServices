import requests
from . import creds
import logging

from .BitrixFieldsAliases import *


class BitrixWorker:
    SESSION = requests.session()
    REQUESTS_TIMEOUT = 10
    REQUESTS_MAX_ATTEMPTS = 3
    APP_ACCESS_TOKEN = None
    APP_REFRESH_TOKEN = None
    TOKENS_STORAGE_NAME = 'bitrix_tokens.pickle'

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
                        logging.error(error)
                else:
                    error = 'Bitrix response failed - %s : Attempt: %s,  Called: %s : Request params: %s' \
                            % (a, response.text, custom_error_text, params)
                    logging.error(error)

            except Exception as e:
                error = 'Sending Bitrix api request %s' % e
                logging.error(error)

        return None


    @staticmethod
    def set_district(deal_id, district_code):
        return BitrixWorker._send_request('crm.deal.update', {'id': deal_id, 'fields': {DEAL_DISTRICT_ALIAS: district_code}})


    @staticmethod
    def get_district_field_data():
        return BitrixWorker._send_request('crm.deal.userfield.get', {'id': DEAL_DISTRICT_FIELD_ID})
