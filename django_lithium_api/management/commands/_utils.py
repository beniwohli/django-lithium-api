# -*- coding: utf-8 -*-
from django.core.management.base import CommandError
from django.utils.functional import wraps

def authenticated(func):
    @wraps(func)
    def auth_wrapper(self, *args, **options):
        if not (options['user'] and options['password']):
            raise CommandError('Please provide a username and password')
        self.api.authenticate(options['user'], options['password'])
        try:
            func(self, *args, **options)
        finally:
            self.api.logout()
    return auth_wrapper