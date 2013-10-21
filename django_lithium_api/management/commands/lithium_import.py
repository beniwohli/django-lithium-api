# -*- coding: utf-8 -*-
from fnmatch import fnmatch

from lxml import etree
from django_lithium_api import signals as api_signals
from django_lithium_api.management.commands._utils import LithiumBaseCommand


class Command(LithiumBaseCommand):
    help = "Handle Lithium event subscriptions"

    def handle_boards_list(self, *args, **options):
        for board in self.api('boards_nested'):
            print """
Title:\t%s
ID:\t%s
href:\t%s
Style:\t%s
            """ % (board.title.encode('utf-8'), board.id, board.href, board.interaction_style)

    def handle_messages(self, *args, **options):
        page_size = 100
        board_id = args[1]
        if '*' in board_id or '?' in board_id:
            boards = [board.id for board in self.api('boards_nested') if fnmatch(board.id, board_id)]
        else:
            boards = [board_id]
        for board in boards:
            page = 1
            messages = self.get_messages(board, page, page_size)
            while messages:
                for message in messages:
                    api_signals.message_create.send(self, message=message, token=None, raw_xml=etree.tostring(message._tree))
                if len(messages) <= page_size:
                    # turns out lithium just keeps returning the results of the very last page, no matter what page
                    # number we use
                    break
                page += 1
                messages = self.get_messages(board, page, page_size)


    def get_messages(self, board, page, page_size):
        return self.api('messages_linear', full_detail=True,  board_id=board, data={'page_size': page_size, 'page': page})