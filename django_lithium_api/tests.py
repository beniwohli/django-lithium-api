# -*- coding: utf-8 -*-
from django.test import TestCase

from django_lithium_api.api import LithiumApi

class LithiumTestCase(TestCase):

    def setUp(self):
        self.api = LithiumApi()


class LithiumAuthenticationTest(LithiumTestCase):
    def test_login(self):
        print self.api.authenticate('piquadrat', '')
        print self.api('auth_user')
        print self.api('auth_logout')


class LithiumEventsTest(LithiumTestCase):

    def test_list(self):
        event_manager = self.api('events')
        print event_manager.__dict__

class LithiumTypeTest(LithiumTestCase):

    def test_board_list(self):
        boards = self.api('boards_nested')
        for board in boards:
            print board.owner