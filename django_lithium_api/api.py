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
    def __init__(self, entry_point=None):
        self.entry_point = entry_point or lithium_settings.get('ENTRY_POINT')
        self.session_key = ''
        if lithium_settings.get('HTTP_USER'):
            auth = (lithium_settings.get('HTTP_USER'), lithium_settings.get('HTTP_PASSWORD'))
        else:
            auth = ()
        if lithium_settings.get('DEBUG'):
            config =  {'verbose': sys.stderr}
        else:
            config = {}
        self.session = requests.session(auth=auth, config=config)

    def authenticate(self, username, password):
        self.session_key = self('auth_login', {'user.login': username, 'user.password': password})

    def logout(self):
        if self.session_key:
            self('auth_logout')
            self.session_key = None

    def __call__(self, method, data=None, **kwargs):
        if data is None:
            data = {}
        if self.session_key:
            data['restapi.session_key'] = self.session_key
        if method in API_PATHS['GET']:
            handler = self.session.get
            request_kwargs = {'params': data}
            path = API_PATHS['GET'][method]
        elif method in API_PATHS['POST']:
            handler = self.session.post
            request_kwargs = {'data': data}
            path = API_PATHS['POST'][method]
        else:
            raise exceptions.MethodNotSupported(method)
        try:
            path = path % kwargs
        except KeyError as e:
            raise exceptions.ArgumentsMissing(e.message)
        url = self.entry_point + path
        response = handler(url, **request_kwargs)
        return self.handle_response(response.content)

    def get_obj_from_url(self, url):
        params = {}
        if self.session_key:
            params['restapi.session_key'] = self.session_key
        url = self.entry_point[:-1] + url
        response = self.session.get(url, params=params)
        return self.handle_response(response.content)

    def handle_response(self, response):
        if lithium_settings.get('DEBUG'):
            print response
        if response:
            tree = etree.fromstring(response)
            if tree.get('status') == 'success':
                elem = tree.getchildren()
                if not elem:
                    return None
                elem = elem[0]
                return types.xml_to_type(elem, self)
            else:
                raise exceptions.RemoteException(response)

api = LithiumApi()