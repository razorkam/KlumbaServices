import xml.etree.ElementTree as ET
import time
import logging
from io import BytesIO

from source.retail_feedback.InvoiceXmlDefs import *
from source.retail_feedback.RFBitrixWorker import *
from source.RunnableService import RunnableService
import source.retail_feedback.Utils as Utils

logger = logging.getLogger(__name__)


class RetailFeedback(RunnableService):
    CHECK_INTERVAL = 60  # seconds

    @staticmethod
    def get_attrib_val(key, attribs):
        if key in attribs:
            return attribs[key]

        return None

    @staticmethod
    def handle_files():
        files = RFBitrixWorker.get_available_files()

        if files:
            logger.info("%s retail feedback files available now", len(files))

        for f in files:
            response = RFBitrixWorker.get_file_content(f.url)
            if not response:
                return

            bstream = BytesIO(response.content)
            xml_tree = ET.parse(bstream)
            root = xml_tree.getroot()
            result = RetailFeedback.parse_file(root)

            if result:
                RFBitrixWorker.move_to(f.id, ARCHIVED_FOLDER_ID)
                logger.info("File with ID %s has been processed, archiving now!", f.id)
            else:
                RFBitrixWorker.move_to(f.id, ERROR_FOLDER_ID)
                logger.info("File with ID %s processing failed, moving to errors storage", f.id)


    @staticmethod
    def parse_file(xml_root):
        try:
            if xml_root.tag == ROOT_TAG:
                for child in xml_root:
                    if child.tag == INVOICE_TAG:
                        attribs = child.attrib

                        code = RetailFeedback.get_attrib_val(CODE, attribs)
                        fullname = RetailFeedback.get_attrib_val(FULL_NAME, attribs)
                        phone = RetailFeedback.get_attrib_val(PHONE, attribs)
                        firstname = RetailFeedback.get_attrib_val(FIRST_NAME, attribs)
                        lastname = RetailFeedback.get_attrib_val(LAST_NAME, attribs)
                        patrname = RetailFeedback.get_attrib_val(PATR, attribs)
                        sex = RetailFeedback.get_attrib_val(SEX, attribs)
                        birthday = RetailFeedback.get_attrib_val(BIRTHDAY, attribs)
                        date = RetailFeedback.get_attrib_val(INVOICE_DATE, attribs)
                        warehouse = RetailFeedback.get_attrib_val(WAREHOUSE, attribs)
                        deal_sum = RetailFeedback.get_attrib_val(SUM, attribs)

                        # find contact by name, surname, patrname and phone
                        # if no - create
                        # create deal with this contact

                        contact_id = RFBitrixWorker.get_contact_id(firstname, lastname, patrname, fullname,
                                                                   phone, birthday, sex)

                        if not contact_id:
                            logger.error('File handling error: no contact for deal')
                            return False

                        deal_add_params = {
                            DEAL_1C_CODE_ALIAS: code,
                            DEAL_WAREHOUSE_ALIAS: Utils.map_warehouse_to_list_elt_id(warehouse),
                            DEAL_CONTACT_IDS_ALIAS: [contact_id],
                            DEAL_SUM_ALIAS: Utils.prepare_numeric(deal_sum),
                            DEAL_DATE_ALIAS: Utils.prepare_date(date),
                            DEAL_CATEGORY_ALIAS: DEAL_DEFAULT_CATEGORY_ID,
                            DEAL_SOURCE_ALIAS: DEFAULT_SOURCE,
                            DEAL_DELIVERY_TYPE_ALIAS: DEAL_DEFAULT_DELIVERY_TYPE,
                            UTM_SOURCE_MARK_ALIAS: UTM_SOURCE_MARK_DEFAULT
                        }

                        result = RFBitrixWorker.add_deal(deal_add_params)
                        if not Utils.is_numeric(result):
                            return False
                return True
            return False
        except Exception as e:
            logger.error("Error parsing file: %s", e)
            return False

    @staticmethod
    def run():
        while True:
            try:
                RetailFeedback.handle_files()
                time.sleep(RetailFeedback.CHECK_INTERVAL)
            except Exception as e:
                logger.error("RetailFeedback global error: %s", e)
