# -*- coding: utf-8 -*-
import pprint

from collections import defaultdict, OrderedDict

from dateutil.parser import  parse as parse_datetime
from lxml import etree


class LithiumType(object):
    def __init__(self, xml_tree, api):
        self.id = xml_tree.get('id')
        self.href = xml_tree.get('href')
        self._tree = xml_tree
        self._populated = False
        self._api = api

        for child in xml_tree:
            if hasattr(self, '_handle_%s' % child.tag):
                getattr(self, '_handle_%s' % child.tag)(child)
            else:
                setattr(self, child.tag, xml_to_type(child, api))

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError(item)
        if self._api and self.href and not self._populated:
            obj = self._api.raw(self.href)
            self.__dict__.update(obj.__dict__)
        self._populated = True
        if item in self.__dict__:
            return getattr(self, item)
        else:
            raise AttributeError(item)

    def __repr__(self):
        return '<%s>: %s' % (self.__class__.__name__, pprint.pformat({k:v for k, v in self.__dict__.iteritems() if not k.startswith('_')}))


class Board(LithiumType):
    pass


class Blog(LithiumType):
    pass


class Category(LithiumType):
    pass


class User(LithiumType):
    pass


class Message(LithiumType):
    pass


class MessageStatus(LithiumType):
    pass


class Label(LithiumType):
    pass


class Thread(LithiumType):
    def _handle_messages(self, child):
        """
        ``<messages>`` has a somewhat nonstandard structure::

            <messages>
                <topic type="message" href="/messages/id/123" /> <!-- first message in thread -->
                <read> <!-- read count (?) -->
                    <count type="int">5</count>
                </read>
                <linear> <!-- list of messages -->
                    <!-- note: first message is equal to topic -->
                    <message type="message" href="/messages/id/123" />
                    <message type="message" href="/messages/id/124" />
                    <message type="message" href="/messages/id/125" />
                </linear>
            </messages>
        """

        messages = OrderedDict()
        for elem in child:
            if elem.tag == 'topic':
                self.topic = xml_to_type(elem, self._api)
                messages[self.topic.href] = self.topic
            elif elem.tag == 'linear':
                for message in elem:
                    m = xml_to_type(message, self._api)
                    if m.href not in messages:
                        messages[m.href] = m
                    if m.parent and m.parent.href in messages:
                        m.parent = messages[m.parent.href]
            elif elem.tag == 'read':
                self.read_count = elem.text
        self.messages = messages.values()


class EventSubscriptionManager(LithiumType):
    pass

class EventSubscription(LithiumType):

    def __unicode__(self):
        return u"""Type:\t\t%s
Callback:\t%s
Token:\t\t%s""" % (self.event_type, self.callback_url, self.token)


# this maps lithium primitive types to python types. For the most part,
# it leaves them as-is -- unicode strings.

primitive_type_map = defaultdict(lambda: lambda value: value.strip() if value else value, {
    'boolean': lambda value: value == 'true',
    'double': float,
    'float': float,
    'int': int,
    'long': long,
    'date_time': parse_datetime,
})

def primitive_type(xml_tree):
    if xml_tree.getchildren():
        raise ValueError('this is not a primitive type:\n%s' % etree.tostring(xml_tree))
    return primitive_type_map[xml_tree.get('type')](xml_tree.text)

def xml_to_type(xml_tree, api=None):
    """
    recursive function to turn an XML response from the REST API into
    python objects
    """
    lithium_type = xml_tree.get('type')
    if xml_tree.attrib.get('null') == 'true':
        return None
    if lithium_type in types_map:
        # this is a complex type
        lithium_type = types_map.get(xml_tree.get('type'))
        return lithium_type(xml_tree, api)
    elif lithium_type is None:
        # this is a list or dictionary
        children = xml_tree.getchildren()
        if not children:
            # empty, can't say if list or dictionary
            return []
        if 'name' in children[0].attrib:
            # it's a dictionary
            result = {}
            for child in xml_tree.getchildren():
                result[child.get('name')] = xml_to_type(child, api)
        else:
            # it's a list
            result = []
            for child in xml_tree.getchildren():
                result.append(xml_to_type(child, api))
        return result
    else:
        # gotta be a primitive type, then!
        return primitive_type(xml_tree)

types_map = {
    'category': Category,
    'board': Board,
    'blog': Blog,
    'user': User,
    'thread': Thread,
    'message': Message,
    'message_status': MessageStatus,
    'label': Label,

    'event_subscription_manager': EventSubscriptionManager,
    'event_subscription': EventSubscription,

    'value': primitive_type,
}
