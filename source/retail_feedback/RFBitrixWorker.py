import re
import logging
import requests

logger = logging.getLogger(__name__)

from source.BitrixWorker import BitrixWorker
from source.retail_feedback.BitrixFieldAliases import *
from source.retail_feedback.BitrixFieldMappings import *
import source.retail_feedback.Utils as Utils

class DataFile:
    id = None
    url = None

    def __init__(self, file_id, file_url):
        self.id = file_id
        self.url = file_url

class RFBitrixWorker(BitrixWorker):
    XML_FILE_PATTERN = re.compile('.*\.xml$')

    @staticmethod
    def get_available_files():
        try:
            folder_children = BitrixWorker._send_request('disk.folder.getchildren',
                                                         {'id': UPLOAD_1C_FOLDER_ID})
            if not folder_children:
                return []

            files_list = []

            for elt in folder_children:
                if elt[DISK_ENTITY_TYPE_ALIAS] == DISK_FILE_TYPE and re.match(RFBitrixWorker.XML_FILE_PATTERN,
                                                                              elt[DISK_FILE_NAME_ALIAS]):
                    file = DataFile(elt[DISK_FILE_ID_ALIAS], elt[DISK_FILE_DL_URL_ALIAS])
                    files_list.append(file)

            return files_list
        except Exception as e:
            logger.error('Error getting download urls for RF files: %s', e)
            return []

    @staticmethod
    def get_file_content(url):
        for a in range(BitrixWorker.REQUESTS_MAX_ATTEMPTS):
            try:
                response = requests.get(url, timeout=BitrixWorker.REQUESTS_TIMEOUT)

                if response and response.ok:
                    return response
                else:
                    logger.error('Downloading file bad response attempt %s : URL: %s ', a, url)

            except Exception as e:
                logger.error('Downloading file: %s', e)

        return None

    @staticmethod
    def get_contact_id(firstname, lastname, patrname, fullname, phone, birthdate, sex):
        try:
            if firstname:
                name = firstname
            else:
                name = fullname
                lastname = None
                patrname = None

            phone = Utils.prepare_phone(phone)

            search_params = {
                'select': [CONTACT_ID_ALIAS],
                'filter': {
                    CONTACT_PHONE_ALIAS: phone,
                    CONTACT_NAME_ALIAS : name,
                    CONTACT_PATR_ALIAS: patrname,
                    CONTACT_LAST_NAME_ALIAS: lastname
                }
            }

            response = BitrixWorker._send_request('crm.contact.list', search_params)
            contact_id = None

            if response:
                contact_id = response[0][CONTACT_ID_ALIAS]
            else:
                create_params = {
                    CONTACT_PHONE_ALIAS: [{
                        CONTACT_PHONE_VALUE_ALIAS: phone,
                        CONTACT_PHONE_TYPE_ALIAS: CONTACT_PHONE_DEFAULT_TYPE
                    }],
                    CONTACT_NAME_ALIAS: name,
                    CONTACT_PATR_ALIAS: patrname,
                    CONTACT_LAST_NAME_ALIAS: lastname,
                    CONTACT_TYPE_ALIAS: CONTACT_DEFAULT_TYPE,
                    CONTACT_BIRTHDAY_ALIAS: Utils.prepare_date(birthdate),
                    CONTACT_SEX_ALIAS: Utils.map_sex_to_list_elt_id(sex),
                    CONTACT_SOURCE_ALIAS: DEFAULT_SOURCE,
                    UTM_SOURCE_MARK_ALIAS: UTM_SOURCE_MARK_DEFAULT
                }

                create_response = BitrixWorker._send_request('crm.contact.add',
                                                             {'fields': create_params})

                contact_id = create_response

        except Exception as e:
            logger.error('Getting contact id %s', e)
            contact_id = None

        return contact_id


    @staticmethod
    def add_deal(params):
        return BitrixWorker._send_request('crm.deal.add',
                                          {'fields': params})


    @staticmethod
    def move_to(file_id, target_dir_id):
        try:
            result = RFBitrixWorker._send_request('disk.file.moveto', {
                'id': file_id,
                'targetFolderId': target_dir_id
            })

            if 'ID' not in result:
                logger.error('Error moving file %s', file_id)

        except Exception as e:
            logger.error('Error moving file %s', file_id)

