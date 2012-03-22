# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

EVENTS = (
    ('MessageCreate', _('message created')),
    ('MessageUpdate', _('message updated')),
    ('MessageMove', _('message moved')),
    ('MessageDelete', _('message deleted')),
    ('UserCreate', _('user created')),
    ('UserUpdate', _('user updated')),
    ('UserSignOn', _('user signed on')),
    ('UserSignOff', _('user signed off')),
)

INTERACTION_STYLES = (
    ('board', _('Board')),
    ('blog', _('Blog')),
    ('idea', _('Ideas')),
    ('contest', _('Contest')),
    ('qanda', _('Q & A')),
    ('tkb', _('Knowledge Base')),
    ('media', _('Media'))
)

BOARD_INTERACTION_STYLES = (
    ('board', _('Board')),
    ('blog', _('Blog')),
    ('idea', _('Ideas')),
    ('tkb', _('Knowledge Base')),
)

DISCUSSION_STYLES = (
    ('forum', _('Forum')),
    ('blog', _('Blog')),
    ('idea', _('Ideas')),
    ('tkb', _('Knowledge Base')),
)