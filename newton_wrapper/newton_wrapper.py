import hmac
import requests
import socketio
from datetime import datetime
from base64 import b64encode
from math import floor
from hashlib import sha256

from .utils import response_to_json, convert_to_timestamp


ENCODING = "utf-8"
BASE_URL = "https://api.newton.co/v1"
WS_BASE_URL = "https://ws.newton.co"


class Newton:

    class ActionType():
        DEPOSIT = "DEPOSIT"
        WITHDRAWAL = "WITHDRAWAL"
        TRANSACT = "TRANSACT"
        ALL = ""

    class TimeInForce():
        IOC = "IOC"
        GTC = "GTC"
        GTD = "GTD"
        NONE = ""

    def __init__(self, client_id=None, secret_key=None):
        self.__client_id = client_id
        self.__secret_key = secret_key
        self.__sio = None
        self.__feed = None

    def __generate_signature_date(self, method, path, content_type="", body=""):

        assert self.__client_id, "Set client id when using private requests"
        assert self.__secret_key, "Set secret key when using private requests"

        current_time = str(floor(datetime.now().timestamp()))

        # If the request has a body, you would use this instead of empty string below (replace BODY with actual request body):
        if body != "":
            hashed_body = sha256(body.encode(ENCODING)).hexdigest()
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
            self.__secret_key.encode(ENCODING),
            msg=signature_data,
            digestmod=sha256
        ).digest()

        NewtonAPIAuth = self.__client_id + ":" + \
            b64encode(computed_signature).decode()
        NewtonDate = current_time

        return [NewtonAPIAuth, NewtonDate]

    def set_client_id(self, client_id):
        self.__client_id = client_id

    def set_secret_key(self, secret_key):
        self.__secret_key = secret_key

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
    def get_actions(self, action_type: ActionType = ActionType.ALL, start_date="", end_date="", limit="", offset=""):
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

    def get_order_history(self, start_date="", end_date="", limit="", offset="", symbol="", time_in_force: TimeInForce = TimeInForce.NONE):
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

    def get_open_orders(self, limit="", offset="", symbol="", time_in_force: TimeInForce = TimeInForce.NONE):
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

    # order_type = ["LIMIT"]
    # side = ["BUY", "SELL"]
    # Open order: {'order_type': ['This field is required.'], 'time_in_force': ['This field is required.'], 'side': ['This field is required.'], 'symbol': ['This field is required.'], 'quantity': ['This field is required.'], 'price': ['This field is required.']}
    def new_order(self, order_type, side, symbol, quantity, price, time_in_force: TimeInForce = TimeInForce.NONE):
        body = '{"order_type":"'+str(order_type)+'", "time_in_force":"'+str(time_in_force)+'", "side":"' + \
            str(side)+'", "symbol":"'+str(symbol)+'","quantity":"' + \
            str(quantity)+'","price":"'+str(price)+'"}'

        NewtonAPIAuth, NewtonDate = self.__generate_signature_date(
            "POST", "/order/new", "application/json", body)
        headers = {'NewtonAPIAuth': NewtonAPIAuth,
                   'NewtonDate': NewtonDate, 'Content-type': 'application/json'}

        r = requests.post(BASE_URL + "/order/new", headers=headers, data=body)
        return response_to_json(r.text)

    # order_id = UUID
    def cancel_order(self, order_id):
        body = '{"order_id":"'+str(order_id)+'"}'

        NewtonAPIAuth, NewtonDate = self.__generate_signature_date(
            "POST", "/order/cancel", "application/json", body)
        headers = {'NewtonAPIAuth': NewtonAPIAuth,
                   'NewtonDate': NewtonDate, 'Content-type': 'application/json'}

        r = requests.post(BASE_URL + "/order/cancel",
                          headers=headers, data=body)
        return response_to_json(r.text)

    def subscribe_to_feed(self, ns, symbol, candle=None):
        self.disconnect_from_feed()
        sio = socketio.Client()
        self.__sio = sio

        @sio.on('connect', namespace=ns)
        def on_connect():
            sio.emit('subscribe', namespace=ns)

        @sio.event
        def connect_error(message=None):
            print('connection failed ', message)

        @sio.event(namespace=ns)
        def update(data):
            self.__feed = data

        url = WS_BASE_URL + ns + '/?symbol=' + symbol
        if candle:
            url += '&candle=' + candle
        sio.connect(url, namespaces=[ns],  transports=['websocket'])

    def get_feed(self):
        return self.__feed

    def disconnect_from_feed(self):
        if self.__sio:
            self.__sio.disconnect()
            self.__sio = None
            self.__feed = None
