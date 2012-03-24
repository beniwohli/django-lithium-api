# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.management import CommandError
from django_lithium_api.management.commands._utils import authenticated, LithiumBaseCommand


class Command(LithiumBaseCommand):
    help = "Handle Lithium event subscriptions"

    option_list = LithiumBaseCommand.option_list + (
        make_option('--callback', dest='callback', type='string', default='',
            help='The callback URL for the event subscription'),
    )

    @authenticated
    def handle_list_subscriptions(self, *args, **options):
        print "Active Subscriptions\n"
        for subscription in self.api('events_subscriptions'):
            print unicode(subscription)
            print

    def handle_types(self, *args, **options):
        for event in self.api('events_types'):
            print event

    @authenticated
    def handle_subscribe(self, *args, **options):
        if not options['callback']:
            raise CommandError('No callback URL provided')
        if len(args) < 2:
            raise CommandError('No event type provided. Run "lithium_events types" to check what\'s available')
        event_types = self.api('events_types')
        for arg in args[1:]:
            if arg not in event_types:
                raise CommandError('Event type "%s" not known. Run "lithium_events types" to check what\'s available' % args)
        for arg in args[1:]:
            print self.api('events_subscribe', data={'event.callback_url': options['callback']}, event_type=arg)

    @authenticated
    def handle_unsubscribe(self, *args, **options):
        if len(args) < 2:
            raise CommandError('No event token provided. Run "lithium_events list_subscriptions" to check active subscriptions')
        if args[1] == 'all':
            print self.api('events_unsubscribe_all')
        else:
            for arg in args[1:]:
                print self.api('events_unsubscribe', subscription_token=arg)
