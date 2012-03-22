# -*- coding: utf-8 -*-

DEFAULT_SETTINGS = {
    'ENTRY_POINT': 'https://lithosphere.lithium.com/lithium/restapi/vc/',
    'HTTP_USER': None,
    'HTTP_PASSWORD': None,

    'DEBUG': False,
}

def get(setting_name):
    from django.conf import settings
    return getattr(settings, 'LITHIUM_API_' + setting_name, DEFAULT_SETTINGS[setting_name])