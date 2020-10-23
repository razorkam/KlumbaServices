import re
import datetime
import logging

from source.retail_feedback.BitrixFieldMappings import *

logger = logging.getLogger(__name__)
PHONE_INVALID_CHARS_PATTERN = re.compile('[^+\d]')
NUMERIC_INVALID_CHARS_PATTERN = re.compile('[^.\d]')
ID_VALID_PATTERN = re.compile('^\d+$')
MIN_VALID_DATETIME = datetime.datetime.strptime('01.01.1901 00:00:00 +0300', '%d.%m.%Y %H:%M:%S %z')
SOURCE_DECIMAL_DELIM = ','
TARGET_DECIMAL_DELIM = '.'

def prepare_phone(phone):
    if not phone:
        return None

    return re.sub(PHONE_INVALID_CHARS_PATTERN, '', phone)

# "1995-06-30T03:00:00+04:00" - result
# "21.10.2020 13:06:39" - source
def prepare_date(date):
    try:
        dt = datetime.datetime.strptime(date + ' +0300', '%d.%m.%Y %H:%M:%S %z')

        if dt < MIN_VALID_DATETIME:
            raise ValueError('Datetime %s is too small!', dt)

        return dt.isoformat()
    except Exception as e:
        logger.error("Error parsing date XMl->Bitrix ISO: %s", e)
        return None

def prepare_numeric(val):
    try:
        delimeter_replaced = val.replace(SOURCE_DECIMAL_DELIM, TARGET_DECIMAL_DELIM)
        result = re.sub(NUMERIC_INVALID_CHARS_PATTERN, '', delimeter_replaced)
        return float(result)
    except Exception as e:
        logger.error('Preparing numeric: %s', e)
        return None

def is_numeric(val):
    try:
        return str(val).isdecimal()
    except Exception as e:
        logger.error('Checking value if is numeric: %s', e)
        return False

def map_sex_to_list_elt_id(sex):
    if sex in SEX_TO_LIST_ELT_ID:
        return SEX_TO_LIST_ELT_ID[sex]

    logger.error("Error mapping sex: %s", sex)
    return None

def map_warehouse_to_list_elt_id(warehouse):
    if warehouse in WAREHOUSE_TO_LIST_ELT_ID:
        return WAREHOUSE_TO_LIST_ELT_ID[warehouse]

    logger.error("Error mapping warehouse: %s", warehouse)
    return None