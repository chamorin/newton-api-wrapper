import os
import hmac
import requests
from datetime import datetime
from base64 import b64encode
from math import floor
from hashlib import sha256

from src.utils import response_to_json, convert_to_timestamp

ENCODING = "utf-8"
BASE_URL = "https://api.newton.co/v1"


class NewtonAPI:

    def __init__(self, client_id, secret_key):
        self.client_id = client_id
        self.secret_key = secret_key

    def __generate_signature_date(self, method, path, content_type="", body=""):

        current_time = str(floor(datetime.now().timestamp()))

        # If the request has a body, you would use this instead of empty string below (replace BODY with actual request body):
        if body != "":
            hashed_body = sha256(body).hexdigest()
        else:
            hashed_body = body

        signature_parameters = [
            method,  # HTTP Method
            content_type,  # Content Type
            "/v1" + path,  # Request URI
            hashed_body,  # If the request has a body, this would be hashed_body
            current_time
        ]

        signature_data = ":".join(signature_parameters).encode(ENCODING)

        computed_signature = hmac.new(
            self.secret_key.encode(ENCODING),
            msg=signature_data,
            digestmod=sha256
        ).digest()

        NewtonAPIAuth = self.client_id + ":" + \
            b64encode(computed_signature).decode()
        NewtonDate = current_time

        return [NewtonAPIAuth, NewtonDate]

    # PUBLIC requests
    def get_fees(self):
        r = requests.get(BASE_URL + "/fees")
        return response_to_json(r.text)

    def healthcheck(self):
        r = requests.get(BASE_URL + "/health-check")
        return 'UP' if r.status_code == 200 else 'DOWN'

    def get_max_trade(self):
        r = requests.get(BASE_URL + "/order/maximums")
        return response_to_json(r.text)

    def get_min_trade(self):
        r = requests.get(BASE_URL + "/order/minimums")
        return response_to_json(r.text)

    def get_tick_sizes(self):
        r = requests.get(BASE_URL + "/order/tick-sizes")
        return response_to_json(r.text)

    def get_symbols(self, base_asset="", quote_asset=""):
        params = {'base_asset': base_asset, 'quote_asset': quote_asset}
        r = requests.get(BASE_URL + "/symbols", params=params)
        return response_to_json(r.text)

    # PRIVATE requests
    def get_actions(self, action_type="DEPOSIT", start_date="", end_date="", limit=1, offset=1):
        NewtonAPIAuth, NewtonDate = self.__generate_signature_date(
            "GET", "/actions")
        headers = {'NewtonAPIAuth': NewtonAPIAuth, 'NewtonDate': NewtonDate}

        start_date = convert_to_timestamp(start_date)
        end_date = convert_to_timestamp(end_date)

        params = {
            'action_type': action_type, 'start_date': start_date,
            'end_date': end_date, 'limit': limit, 'offset': offset
        }

        r = requests.get(BASE_URL + "/actions", headers=headers, params=params)
        return response_to_json(r.text)

    def get_balances(self, asset=""):
        NewtonAPIAuth, NewtonDate = self.__generate_signature_date(
            "GET", "/balances")
        headers = {'NewtonAPIAuth': NewtonAPIAuth, 'NewtonDate': NewtonDate}

        params = {'asset': asset}
        r = requests.get(BASE_URL + "/balances",
                         headers=headers, params=params)
        return response_to_json(r.text)

    def get_order_history(self, start_date="", end_date="", limit=1, offset=1, symbol="", time_in_force=""):
        NewtonAPIAuth, NewtonDate = self.__generate_signature_date(
            "GET", "/order/history")
        headers = {'NewtonAPIAuth': NewtonAPIAuth, 'NewtonDate': NewtonDate}

        start_date = convert_to_timestamp(start_date)
        end_date = convert_to_timestamp(end_date)

        params = {
            'start_date': start_date, 'end_date': end_date, 'limit': limit,
            'offset': offset, 'symbol': symbol, 'time_in_force': time_in_force
        }

        r = requests.get(BASE_URL + "/order/history",
                         headers=headers, params=params)
        return response_to_json(r.text)

    def get_open_orders(self, limit=1, offset=1, symbol="", time_in_force=""):
        NewtonAPIAuth, NewtonDate = self.__generate_signature_date(
            "GET", "/order/open")
        headers = {'NewtonAPIAuth': NewtonAPIAuth, 'NewtonDate': NewtonDate}

        params = {
            'limit': limit, 'offset': offset,
            'symbol': symbol, 'time_in_force': time_in_force
        }

        r = requests.get(BASE_URL + "/order/open",
                         headers=headers, params=params)
        return response_to_json(r.text)

    def new_order(self, limit=1, offset=1, symbol="", time_in_force=""):
        NewtonAPIAuth, NewtonDate = self.__generate_signature_date(
            "POST", "/order/new")
        headers = {'NewtonAPIAuth': NewtonAPIAuth, 'NewtonDate': NewtonDate}

        params = {
            'limit': limit, 'offset': offset,
            'symbol': symbol, 'time_in_force': time_in_force
        }

        r = requests.post(BASE_URL + "/order/open",
                          headers=headers, params=params)
        return response_to_json(r.text)
