import logging
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache

import requests

logger = logging.getLogger('devino.client')


class DevinoError(Exception):
    """Общая ошибка devino.
    """
    pass


class DevinoRequestError(DevinoError):
    def __init__(self, *args):
        self.args = args


class NetworkError(DevinoError):
    """Сетевая ошибка. 

    Не ошибка бизнес логики. Запрос с данной ошибкой может быть повторно 
    отправлен.
    """
    pass


class TimeoutError(NetworkError):
    """Таймаут при выполнении запроса-ответа.
    """
    pass


class RestApi(object):
    """
    Class for calling REST API methods

    https://github.com/devinotelecom/sms-restapi-python
    """

    # время жизни токена составляет 2 часа: http://docs.devinotele.com/httpapi.html#id2
    SESSION_LIVE_TIMEOUT = 2 * 60 * 60

    # ключ для записи токена в cache
    CACHE_SESSION_KEY = 'devinotele:session_id'

    def __init__(self, login, password, host='https://integrationapi.net/rest'):
        self._login = login
        self._password = password
        self._host = host
        self._get_session_id()

    def _get_session_id(self):
        """ get session identifier
        """
        logger.info('Get session_id from cache')
        self._session_id = self.get_cached_session()

        if self._session_id is None:
            logger.info('Has no session_id')
            self.renew_session()

        logger.info('Use session_id, %s', self._session_id)
        return self._session_id

    @classmethod
    def get_cached_session(cls):
        """
        Получение токена из кеша 
        """
        return cache.get(cls.CACHE_SESSION_KEY)

    def renew_session(self):
        """
        Запрос на получение session_id.
        Обновляем сессию и записываем в cache
        """

        logger.info('Renew session_id')
        params = urlencode({'login': self._login, 'password': self._password})
        response = requests.get(
            '{0}/user/sessionId?{1}'.format(self._host, params),
            timeout=settings.SMS_SERVICE_TIMEOUT_SEC)

        if response.status_code != 200:
            raise DevinoRequestError('Cannot get sessionID from devino')

        self._session_id = response.json()

        cache.set(self.CACHE_SESSION_KEY, self._session_id, self.SESSION_LIVE_TIMEOUT)
        logger.info('session_id has been renewed. %s', self._session_id)

    def get_balance(self):
        """ get balance
        """
        return self._request("/user/balance?")

    def send_message(self, source_address, destination_address,
                     data, validity=0, send_date_utc=''):
        """ send message
        """

        logger.info('Send new message to %s', destination_address)
        params = {'sourceAddress': source_address,
                  'destinationAddress': destination_address,
                  'data': data,
                  'validity': validity,
                  'sendDate': send_date_utc}
        return self._request("/sms/send", params, 'post')

    def send_messages_bulk(self, source_address, destination_addresses,
                           data, validity=0, send_date_utc=''):
        """ send messages to many addresses
        """
        params = {'sourceAddress': source_address,
                  'destinationAddresses': destination_addresses,
                  'data': data,
                  'validity': validity,
                  'sendDate': send_date_utc}
        return self._request("/sms/sendbulk", params, 'post')

    def send_message_by_timezone(self, source_address, destination_address,
                                 data, send_date, validity=0):
        """ send message in addressee local time, send_date should be local time
        """
        params = {'sourceAddress': source_address,
                  'destinationAddress': destination_address,
                  'data': data,
                  'validity': validity,
                  'sendDate': send_date}
        return self._request("/sms/sendbytimezone", params, 'post')

    def get_message_state(self, message_id):
        """ getting state for message by its identifier
        """
        params = {'messageId': message_id}
        return self._request("/sms/state?", params)

    def get_statistics(self, start_date, end_date):
        """ getting sent/delivered statistics in datetime range,
        datetimes should be local
        """
        params = {'startDateTime': start_date,
                  'endDateTime': end_date}
        return self._request("/sms/statistics?", params)

    def get_incoming_messages(self, start_date_utc, end_date_utc):
        """ getting incoming messages in datetime range,
        datetimes should be UTC
        """
        params = {'minDateUTC': start_date_utc,
                  'maxDateUTC': end_date_utc}
        return self._request("/sms/in?", params)

    def _request(self, path, params=None, method='get'):
        if not params:
            params = {}
        params['sessionId'] = self._session_id
        path = self._host + path

        try:
            logger.info(u"Devinotele request: {path}; data: {params}".format(path=path, params=params))
            encoded_params = urlencode(params, True)

            if method == 'get':
                response = requests.get(path + encoded_params,
                                        timeout=settings.SMS_SERVICE_TIMEOUT_SEC)
            else:
                response = requests.post(path,
                                         json=params,
                                         timeout=settings.SMS_SERVICE_TIMEOUT_SEC)

            if response.status_code == 401:
                self.renew_session()
                params['sessionId'] = self._session_id
                encoded_params = urlencode(params, True)
                if method == 'get':
                    response = requests.get(path + encoded_params,
                                            timeout=settings.DEVINOTELE_TIMEOUT_SEC)
                else:
                    response = requests.post(path,
                                             json=params,
                                             timeout=settings.DEVINOTELE_TIMEOUT_SEC)

        except requests.Timeout:
            logger.exception(u'Timeout error: {}: {}'.format(path, params))
            raise TimeoutError('Request is timed-out')

        return response.json()
