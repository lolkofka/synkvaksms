import logging
import time
from typing import Literal

import requests
from cachetools import TTLCache, cached

from .exceptions import *
from .models import *

cache_all_data = TTLCache(maxsize=100, ttl=3600)  # 1 hour cache
cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour cache
cache_countries = TTLCache(maxsize=100, ttl=3600)  # 1 hour cache


def _send_request(base_url: str, uri: str, **kwargs) -> dict[str, ...]:
    try:
        r = requests.get(base_url+uri, **kwargs)
        response = r.json()
        if not isinstance(response, dict) or not response.get('error'):
            return response
        else:
            raise VakSmsBadRequest(response['error'])
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        raise ValueError('Invalid Base URL')


class Vaksms:
    """
    VakSms client for API interaction
    Session will be automatically closed

    API for https://vak-sms.com/
    """

    def __init__(self, api_key: str,
                 base_url: str | None = None, timeout: int = 10):
        """
        Creates instance of one vaksms API client

        Args:
            api_key: API key from https://vak-sms.com/lk/
            base_url: base URL (Optional)
        """

        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    def get_balance(self) -> float:
        """
        Creates a request for get balances of user
        See https://vak-sms.com/api/vak/

        Returns: float of balance
        """

        response = self.__create_request('/api/getBalance')

        return response['balance']

    @cached(cache)
    def get_count_number(self, service: str, operator: str = None, country: str = 'ru') -> CountNumber:
        """
        Creates a request for get count and price of number
        See https://vak-sms.com/api/vak/
        
        Args:
            service: service to check count
            operator: operator to check count
            country: country to check count
        
        Returns: Model from response JSON
        """

        params = {
            'service': service,
            'operator': operator,
            'country': country,
            'price': 1,
        }

        response = self.__create_request('/api/getCountNumber', params)
        response['service'] = list(response.keys())[0]
        response['count'] = response[list(response.keys())[0]]
        return CountNumber(**response)

    @cached(cache_countries)
    def get_country_list(self) -> list[CountryOperator]:
        """
        Creates a request for get countries and operators inside a country
        See https://vak-sms.com/api/vak/

        Returns: list of Model from response JSON
        """

        response = self.__create_request('/api/getCountryList', api_key_required=False)

        return CountryList(response).root

    def get_number(self, service: str | list, operator: str = None, rent: bool = False, country: str = 'ru',
                         soft_id: str = '1019') -> Number | MultipleResponse:
        """
        Creates a request for buying number
        See https://vak-sms.com/api/vak/
        
        Args:
            service: service to buy number may be list of services to buy 1 number for 2 services
            operator: operator to buy number
            rent: to buy 4 hours - life number
            country: country to buy number
            soft_id: to get referral earnings (set 1019 to support creator this library)
        
        Returns: Model from response JSON
        """

        if isinstance(service, list):
            service = service[0] + ',' + service[1]

        params = {
            'service': service,
            'operator': operator,
            'rent': 'true' if rent else 'false',
            'country': country,
            'softId': soft_id
        }

        response = self.__create_request('/api/getNumber/', params)

        if isinstance(response, list):
            return MultipleResponse(response).root
        else:
            response['service'] = service

        return Number(self, **response, rent=rent)

    def prolong_number(self, service: str, tel: str | int, rent: bool = False,
                             soft_id: str = '1019'):
        """
        Creates a request for buying number
        See https://vak-sms.com/api/vak/

        Args:
            service: service to continuation number
            tel: tel to continuation number, format: 79991112233
            rent: bool need only for set lifetime
            soft_id: to get referral earnings (set 1019 to support creator this library) may be not work in this method

        Returns: Model from response JSON
        """

        params = {
            'service': service,
            'tel': tel,
            'softId': soft_id
        }

        response = self.__create_request('/api/prolongNumber', params)

        response['service'] = service

        return Number(**response, rent=rent)

    def set_status(self, number: str | Number, status: Literal['send', 'end', 'bad']):
        """
        Creates a request for buying number
        statuses:
        send = receiving new sms
        end = cancel the number
        bad = ban the number
        
        the difference between "end" and "bad" is that with bad the number will not come across to other people again,
        including you, I recommend using statuses for their intended purpose so that the numbers do not run out quickly
        and there is enough for everyone
        
        See https://vak-sms.com/api/vak/

        Args:
            number_id: idNum of number
            status: can be set only "send", "end", "bad".

        Returns: status
        """
        
        number_id = number if not type(number) is Number else number.idNum
        params = {
            'idNum': number_id,
            'status': status,
        }

        response = self.__create_request('/api/setStatus', params)

        return response['status']

    def get_sms_code(self, number: str | Number, get_all_numbers: bool | None = None) -> str | list[str]:
        """
        Checking sms codes

        See https://vak-sms.com/api/vak/

        Args:
            number: idNum of number or Number object
            get_all_numbers: set True, to get all sms codes who came on number

        Returns: Model from response JSON, one sms or list of smses
        """
        number_id = number if not type(number) is Number else number.idNum
        if not self._api_key:
            raise ValueError('API key is required for this method')

        params = {
            'idNum': number_id,
            'all': str(get_all_numbers),
        }

        response = self.__create_request('/api/getSmsCode/', params)

        return response
    
    def wait_sms_code(self, number: str | Number, timeout: int = 60*5, per_attempt: int = 5) -> str | None:
        """
        Wait sms code

        Args:
            number_id: idNum of number or Number object
            timeout: maximum time to wait sms code
            per_attempt: time per attempt
            
        Returns: Sms
        """
        number_id = number if not type(number) is Number else number.idNum
        if not self._api_key:
            raise ValueError('API key is required for this method')

        self.set_status(number=number_id, status='send')
        params = {
            'idNum': number_id,
            'all': str(None),
        }

        sms = None
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            time.sleep(per_attempt)
            response = self.__create_request('/api/getSmsCode/', params)
            sms = response['smsCode']
            if type(sms) == list:
                return sms[-1]
        
        return None
        
    @cached(cache_all_data)
    def get_count_number_list(self, country: str = 'RU', operator: str | None = None, rent: bool = False):
        """
        Get all services and prices, count, full name of service

        Its method not in official docs

        Returns: Model from response JSON
        """

        params = {
            'country': country,
        }
        if operator:
            params['operator'] = operator
        params['rent'] = 'True' if rent else 'False',

        response = self.__create_request('/api/getCountNumbersList', params, api_key_required=False)
        ret_d = {}
        for service in response.keys():
            s = Service(**response[service][0])
            s.icon = self._base_url + s.icon
            ret_d[service] = s

        return ret_d

    def __create_request(self, uri: str, params: dict[str, ...] | None = None, api_key_required: bool = True) -> \
            dict[str, ...]:
        """
        Creates a request to base URL and adds URI

        Args:
            uri: URI
            params: Request params (Optional)

        Returns: Model from response JSON
        """

        if api_key_required and not self._api_key:
            raise ValueError('API key is required for this method')

        if params is None:
            params = {}

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        if self._api_key:
            params['apiKey'] = self._api_key

        kwargs = dict(
            headers=headers,
            params={k: v for k, v in params.items() if v is not None},
            timeout=self._timeout
        )

        if self._base_url is None:
            base_urls = ['https://vak-sms.com', 'https://moresms.net', 'https://vaksms.ru']

            for base_url in base_urls:
                try:
                    r = _send_request(base_url, uri, **kwargs)
                    self._base_url = base_url
                    return r
                except ValueError:
                    logging.warning(f'Failed to connect to {base_url}. Specify explicitly working base url')

        return _send_request(self._base_url, uri, **kwargs)
