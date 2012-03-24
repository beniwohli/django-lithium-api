# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management import BaseCommand
from django.core.management.base import CommandError
from django.utils.functional import wraps

from django_lithium_api.api import api as lithium_api


class LithiumBaseCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--user', dest='user', type='string', default='',
            help='The user to use for the connection'),
        make_option('--password', dest='password', type='string', default='',
            help='The password to use for the connection'),
        make_option('--debug', dest='debug', action='store_true', default=False),
    )

    api = lithium_api

    def handle(self, *args, **options):
        self.api.set_debug(options['debug'])
        getattr(self, 'handle_%s' % args[0], self._handle_unknown_command)(*args, **options)

    def _handle_unknown_command(self, *args, **options):
        raise CommandError('subcommand "%s" not known' % args[0])


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