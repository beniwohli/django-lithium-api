# -*- coding: utf-8 -*-

import sys

import requests

from lxml import etree
from django_lithium_api import settings as lithium_settings
from django_lithium_api import exceptions, types


# supported API methods

API_METHODS = {
    'GET': {
        'auth_user_id': 'authentication/sessions/current/id',
        'auth_user': 'authentication/sessions/current/user',

        'boards': 'boards',
        'boards_nested': 'boards/nested',
        'messages_linear': '/boards/id/%(board_id)s/messages/linear',

        'events': 'events',
        'events_types': 'events/types',
        'events_subscriptions': 'events/subscriptions',

    },
    'POST': {
        'auth_login': 'authentication/sessions/login',
        'auth_logout': 'authentication/sessions/logout',

        'events_subscribe': 'events/subscriptions/events/name/%(event_type)s/subscribe',
        'events_unsubscribe': 'events/subscriptions/token/%(subscription_token)s/unsubscribe',
        'events_unsubscribe_all': 'events/subscriptions/users/self/unsubscribe',
    }
}


class LithiumApi(object):
    """
    Initialize the API

    :param entry_point: entry point for the REST API of the form `https://lithosphere.lithium.com/lithium/restapi/vc/`
    :param debug: debug mode.
    """

    def __init__(self, entry_point=None, debug=None):
        self._api_call_count = 0
        self.entry_point = entry_point or lithium_settings.get('ENTRY_POINT')
        self.session_key = ''
        if lithium_settings.get('HTTP_USER'):
            auth = (lithium_settings.get('HTTP_USER'), lithium_settings.get('HTTP_PASSWORD'))
        else:
            auth = ()
        self.session = requests.session(auth=auth, config={})
        self.set_debug(lithium_settings.get('DEBUG') if debug is None else debug)

    def authenticate(self, username, password=None, force_reauth=False):
        """
        Authenticate with the REST API.

        After successfully authenticated, all following API calls automatically
        send the session key.

        :param username: the user name to be used for API calls
        :param password: the password. This can also be set using the ``LITHIUM_API_USERS`` setting
        :param force_reauth: if ``True``, a new authentication token is fetched even if one is available already
        :raise: :class:`~django_lithium_api.exceptions.AuthenticationError`, :class:`django_lithium_api.exceptions.RemoteException`
        """
        if self.session_key and not force_reauth:
            return
        if password is None:
            try:
                password = lithium_settings.get('USERS')[username]
            except KeyError:
                raise exceptions.AuthenticationError('No password set in LITHIUM_API_USERS for "%s".' % username)
        self.session_key = self.call('auth_login', data={'user.login': username, 'user.password': password})

    def logout(self):
        """
        Logs out the user and unsets the session key.
        """

        if self.session_key:
            self.call('auth_logout')
            self.session_key = None

    def call(self, method, full_detail=False, data=None, **kwargs):
        """
        Main entry point to the API.

        :meth:`__call__` is aliased to this method for convenience, so you can
        use the API like this: ``api('boards')``

        :param method: API method as defined in ``API_METHODS``
        :param full_detail: instruct the REST API to return full XML representations
        :param data: POST/GET data to send with the API call
        :param kwargs: arguments to the API call, e.g. event type for ``events_subscribe``
        :return: :class:`None`, :class:`list`, :class:`types.LithiumType`
        :raise: :class:`exceptions.LithiumException` and subclasses.
        """

        if data is None:
            data = {}
        if full_detail:
            data['restapi.format_detail'] = 'full_list_element'
        if method in API_METHODS['GET']:
            http_method = 'get'
            path = API_METHODS['GET'][method]
        elif method in API_METHODS['POST']:
            http_method = 'post'
            path = API_METHODS['POST'][method]
        else:
            raise exceptions.MethodNotSupported(method)
        try:
            path = path % kwargs
        except KeyError as e:
            raise exceptions.ArgumentsMissing(e.message)
        return self.raw(path, http_method, **data)

    __call__ = call

    def raw(self, path, http_method='get', **data):
        """
        Raw access to the REST API.

        :param path: path to the REST API call
        :param http_method: ``"get"`` or ``"post"``
        :param data: GET/POST data
        :return: :class:`None`, :class:`list`, :class:`types.LithiumType`
        """

        if path[0] == '/':
            path = path[1:]
        url = self.entry_point + path
        if self.session_key:
            data['restapi.session_key'] = self.session_key
        if http_method.lower() == 'post':
            handler = self.session.post
            request_kwargs = {'data': data}
        else:
            handler = self.session.get
            request_kwargs = {'params': data}
        self._api_call_count += 1
        response = handler(url, **request_kwargs)
        return self.handle_response(response)

    def handle_response(self, response):
        """
        Handles the response from the REST API and converts it to lithium types
        and primitive types.

        :param response: a :class:`requests.Response` instance.
        :return: :class:`None`, :class:`list`, :class:`types.LithiumType`
        :raise: :class:`~django_lithium_api.exceptions.LithiumException`
        """

        if self._debug:
            sys.stderr.write(response.content)
        if response:
            tree = etree.fromstring(response.content)
            if tree.get('status') == 'success':
                elem = tree.getchildren()
                if not elem:
                    return None
                elem = elem[0]
                return types.xml_to_type(elem, self)
            elif tree.get('status') == 'error':
                error = tree.find('error')
                message = error.findtext('message')
                raise exceptions.RemoteException(message, error.get('code'), response.content)
            else:
                raise exceptions.UnknownResponseType(response.content)

    def set_debug(self, debug):
        """
        Changes the ``debug`` mode of the API. When set to ``True``, HTTP
        requests and XML responses are printed to ``sys.stderr``.

        :param debug: ``True``/``False``
        """

        self._debug = debug
        if debug:
            self.session.config['verbose'] = sys.stderr
        else:
            self.session.config['verbose'] = None

api = LithiumApi()