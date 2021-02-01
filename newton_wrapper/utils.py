import json
import re
from datetime import datetime


def response_to_json(response_text):
    json_content = response_text.splitlines()[-1]
    json_data = json.loads(json_content)
    return json_data


def convert_to_timestamp(date):
    converted_date = None
    if re.match(r'\d{10}(\.\d*)?', str(date)):
        converted_date = int(date)
    elif isinstance(date, datetime):
        converted_date = int(date.timestamp())
    return converted_date
