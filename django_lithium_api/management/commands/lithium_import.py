# -*- coding: utf-8 -*-
from optparse import make_option
from fnmatch import fnmatch

from lxml import etree
from django.core.management import BaseCommand, CommandError
from django_lithium_api.api import api as lithium_api
from django_lithium_api import signals as api_signals
from django_lithium_api.management.commands._utils import authenticated



class Command(BaseCommand):
    help = "Handle Lithium event subscriptions"

    option_list = BaseCommand.option_list + (
        make_option('--user', dest='user', type='string', default='',
            help='The user to use for the connection'),
        make_option('--password', dest='password', type='string', default='',
            help='The password to use for the connection'),
    )

    api = lithium_api

    def handle(self, *args, **options):
        getattr(self, 'handle_%s' % args[0], self._handle_unknown_command)(*args, **options)

    @authenticated
    def handle_boards_list(self, *args, **options):
        for board in self.api('boards_nested'):
            print """
Title:\t%s
ID:\t%s
href:\t%s
Style:\t%s
            """ % (board.title.encode('utf-8'), board.id, board.href, board.interaction_style)

    def handle_messages(self, *args, **options):
        board_id = args[1]
        if '*' in board_id or '?' in board_id:
            boards = [board.id for board in self.api('boards_nested') if fnmatch(board.id, board_id)]
        else:
            boards = [board_id]
        for board in boards:
            for message in self.api('messages_linear', board_id=board):
                api_signals.message_create.send(self, message=message, token=None, raw_xml=etree.tostring(message._tree))

    def _handle_unknown_command(self, *args, **options):
        raise CommandError('subcommand "%s" not known' % args [0])
