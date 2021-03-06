import os
import sys
import time
import json
import hmac
import hashlib
import urllib
import requests

from pathlib import Path  # !Only Python 3.4+(Standart library)
from dotenv import load_dotenv

from flask import Blueprint

# * Create Blueprint
bp = Blueprint('exmo', __name__)


# * Search .env file for this script work
path = Path(os.path.abspath(os.path.dirname(__file__)))
basedir = path.parents[2-1]  # * Level UP 2 directory
load_dotenv(os.path.join(basedir, '.env'))


class ExmoAPI(object):
    """
    Initializes the API requests to
    the cryptocurrency stock exchange Exmo.me
    """

    # API methods:
    commands = {
        # Public API
        'trades'                : {'authenticated': False},  # noqa: E203
        'order_book'            : {'authenticated': False},  # noqa: E203
        'ticker'                : {'authenticated': False},  # noqa: E203
        'pair_settings'         : {'authenticated': False},  # noqa: E203
        'currency'              : {'authenticated': False},  # noqa: E203
        # Authenticated API
        'user_info'             : {'authenticated': True},  # noqa: E203
        'order_create'          : {'authenticated': True},  # noqa: E203
        'order_cancel'          : {'authenticated': True},  # noqa: E203
        'user_open_orders'      : {'authenticated': True},  # noqa: E203
        'user_trades'           : {'authenticated': True},  # noqa: E203
        'user_cancelled_orders' : {'authenticated': True},  # noqa: E203
        'order_trades'          : {'authenticated': True},  # noqa: E203
        'trade_deposit_address' : {'authenticated': True},  # noqa: E203
        # Wallet API
        'wallet_history'        : {'authenticated': True}  # noqa: E203
        }

    def __init__(self, API_KEY='', API_SECRET=''):
        """Announces required parameters"""
        self.API_URL = 'https://api.exmo.me/'
        self.API_VERSION = 'v1/'
        self.API_KEY = API_KEY
        self.API_SECRET = bytes(API_SECRET, encoding='utf-8')

    def __getattr__(self, name):
        """Gets api_method"""
        def wrapper(*args, **kwargs):
            """Gets api_params"""
            kwargs.update(command=name)
            return self.call_api(**kwargs)
        return wrapper

    def sha512(self, data):
        """Encrypts secret key with method HMAC-SHA512"""
        hash_key = hmac.new(key=self.API_SECRET, digestmod=hashlib.sha512)
        hash_key.update(data.encode('utf-8'))
        return hash_key.hexdigest()

    def call_api(self, **kwargs):
        """API request"""
        # Make request to exchange
        command = kwargs.pop('command')
        params = kwargs
        general_uri = self.API_URL + self.API_VERSION + command

        if self.commands[command]['authenticated']:
            method_request = 'POST'
            nonce = {'nonce': int(time.time()*1000)}
            params.update(nonce)
            params_str = urllib.parse.urlencode(params)
            sign = self.sha512(params_str)
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Key": self.API_KEY,
                "Sign": sign,
                }
        else:
            method_request = 'GET'
            params_str = urllib.parse.urlencode(params)

        # Open session
        with requests.Session() as session:
            try:
                if method_request == 'POST':
                    exmo_request = session.post(
                        general_uri,
                        data=params_str,
                        headers=headers)
                if method_request == 'GET':
                    exmo_request = session.get(
                        general_uri + command + '?' + params_str)
            except Exception as error:
                exmo_request = {
                    'result': False,
                    'error': type(error).__name__
                }
                return exmo_request
            finally:
                session.close()

        # Get response
        try:
            response = json.loads(exmo_request.text)
            if 'error' in response and response['error']:
                print(response['error'])
                raise sys.exit()
            return response
        except json.decoder.JSONDecodeError:
            print('Error while parsing response:', response)
            raise sys.exit()


if __name__ == "__main__":
    test_request = ExmoAPI(
        API_KEY=os.environ.get('EXCHANGE_PK') or 'K-pass',
        API_SECRET=os.environ.get('EXCHANGE_SK') or 'S-pass')

    print(json.dumps(
        test_request.user_open_orders(),
        sort_keys=False,
        indent=4,
        separators=(',', ': ')))
