from source.BitrixWorker import BitrixWorker
from source.districts_calc.BitrixFieldsAliases import *


class DCBitrixWorker(BitrixWorker):
    @staticmethod
    def set_district(deal_id, district_code):
        return BitrixWorker._send_request('crm.deal.update', {'id': deal_id,
                                                              'fields': {DEAL_DISTRICT_ALIAS: district_code}})

    @staticmethod
    def get_district_field_data():
        return BitrixWorker._send_request('crm.deal.userfield.get', {'id': DEAL_DISTRICT_FIELD_ID})
