# -*- coding: utf-8 -*-

import sys

import requests

from lxml import etree
from django_lithium_api import settings as lithium_settings
from django_lithium_api import exceptions, types


# supported API methods

API_PATHS = {
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
    def __init__(self, entry_point=None, debug=None):
        self.entry_point = entry_point or lithium_settings.get('ENTRY_POINT')
        self.session_key = ''
        if lithium_settings.get('HTTP_USER'):
            auth = (lithium_settings.get('HTTP_USER'), lithium_settings.get('HTTP_PASSWORD'))
        else:
            auth = ()
        self.session = requests.session(auth=auth, config={})
        self.set_debug(lithium_settings.get('DEBUG') if debug is None else debug)

    def authenticate(self, username, password=None):
        if password is None:
            try:
                password = lithium_settings.get('USERS')[username]
            except KeyError:
                raise exceptions.AuthenticationError('No password set in LITHIUM_API_USERS for "%s".' % username)
        self.session_key = self('auth_login', {'user.login': username, 'user.password': password})

    def logout(self):
        if self.session_key:
            self('auth_logout')
            self.session_key = None

    def __call__(self, method, data=None, **kwargs):
        if data is None:
            data = {}
        if method in API_PATHS['GET']:
            http_method = 'get'
            path = API_PATHS['GET'][method]
        elif method in API_PATHS['POST']:
            http_method = 'post'
            path = API_PATHS['POST'][method]
        else:
            raise exceptions.MethodNotSupported(method)
        try:
            path = path % kwargs
        except KeyError as e:
            raise exceptions.ArgumentsMissing(e.message)
        return self.raw(path, http_method, **data)

    def raw(self, path, http_method='get', **data):
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
        response = handler(url, **request_kwargs)
        return self.handle_response(response)

    def handle_response(self, response):
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
        requests and XML responses are printed to STDERR
        """
        self._debug = debug
        if debug:
            self.session.config['verbose'] = sys.stderr
        else:
            self.session.config['verbose'] = None

api = LithiumApi()