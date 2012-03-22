# -*- coding: utf-8 -*-

from django.dispatch import Signal

msg_providing_args = ['message', 'token', 'raw_xml']
user_providing_args = ['user', 'token', 'raw_xml']

message_create = Signal(providing_args=msg_providing_args)
message_update = Signal(providing_args=msg_providing_args)
message_move = Signal(providing_args=msg_providing_args)
message_delete = Signal(providing_args=msg_providing_args)

user_create = Signal(providing_args=user_providing_args)
user_update = Signal(providing_args=user_providing_args)
user_signon = Signal(providing_args=user_providing_args)
user_signoff = Signal(providing_args=user_providing_args)