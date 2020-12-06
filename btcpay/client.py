"""btcpay.client

BTCPay API Client.
"""

import re
import json
from urllib.parse import urlencode

import requests
from requests.exceptions import HTTPError

class BTCPayClient:
    def __init__(self, host, token, insecure=False):
        self.host = host
        self.token = token
        self.user_agent = 'btcpay-python'
        self.s = requests.Session()
        self.s.headers.update(
            {'Content-Type': 'application/json',
            'accept': 'application/json',
            'X-accept-version': '2.0.0'})

    def create_headers(self):
        return {
            "Authorization": f"Basic {self.token}",
        }

    def _signed_get_request(self, path, params=None):
        uri = self.host + path
        headers = self.create_headers()
        r = self.s.get(uri, params=params, headers=headers)
        r.raise_for_status()
        return r.json()['data']

    def _signed_post_request(self, path, payload):
        uri = self.host + path
        payload = json.dumps(payload)
        headers = self.create_headers()
        r = self.s.post(uri, headers=headers, data=payload)
        if not r.ok:
            if 400 <= r.status_code < 500:
                http_error_msg = u'%s Client Error: \
                        %s for url: %s | body: %s' % (
                            r.status_code,
                            r.reason,
                            r.url,
                            r.text
                        )
            elif 500 <= r.status_code < 600:
                http_error_msg = u'%s Server Error: \
                        %s for url: %s | body: %s' % (
                            r.status_code,
                            r.reason,
                            r.url,
                            r.text
                        )
            if http_error_msg:
                raise HTTPError(http_error_msg, response=r)
        return r.json()['data']

    def _unsigned_request(self, path, payload=None):
        uri = self.host + path
        if payload:
            payload = json.dumps(payload)
            r = self.s.post(uri, data=payload)
        else:
            r = self.s.get(uri)
        r.raise_for_status()
        return r.json()['data']

    def get_rates(self, crypto='BTC', store_id=None):
        params = dict(
            cryptoCode=crypto
        )
        if store_id:
            params['storeID'] = store_id
        return self._signed_get_request('/rates/', params=params)

    def get_rate(self, currency, crypto='BTC', store_id=None):
        rates = self.get_rates(crypto=crypto, store_id=store_id)
        rate = [rate for rate in rates if rate['code'] == currency.upper()][0]
        return rate['rate']

    def create_invoice(self, payload):
        try:
            float(payload['price'])
        except ValueError as e:
            raise ValueError('Price must be a float') from e
        return self._signed_post_request('/invoices/', payload)

    def get_invoice(self, invoice_id):
        return self._signed_get_request('/invoices/' + invoice_id)

    def get_invoices(self, status=None, order_id=None, item_code=None, date_start=None, date_end=None, limit=None, offset=None):
        params = dict()
        if status is not None:
            params['status'] = status
        if order_id is not None:
            params['orderId'] = order_id
        if item_code is not None:
            params['itemCode'] = item_code
        if date_start is not None:
            params['dateStart'] = date_start
        if date_end is not None:
            params['dateEnd'] = date_end
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        return self._signed_get_request('/invoices', params=params)

    def __repr__(self):
        return '{}({})'.format(
            type(self).__name__,
            self.host
        )
