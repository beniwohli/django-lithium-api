# -*- coding: utf-8 -*-
import pprint

from collections import defaultdict

from dateutil.parser import  parse as parse_datetime
from lxml import etree


class LithiumType(object):
    def __init__(self, xml_tree, api):
        self.id = xml_tree.get('id')
        self.href = xml_tree.get('href')
        self._tree = xml_tree
        self._populated = False
        self._api = api

        for child in xml_tree.getchildren():
            setattr(self, child.tag, xml_to_type(child, api))

    def __getattr__(self, item):
        if self._api and self.href and not self._populated:
            obj = self._api.get_obj_from_url(self.href)
            self.__dict__.update(obj.__dict__)
        self._populated = True
        if item in self.__dict__:
            return getattr(self, item)
        else:
            raise AttributeError(item)



    def __repr__(self):
        return pprint.pformat(self.__dict__)


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
    pass


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
        lithium_type = types_map.get(xml_tree.get('type'))
        return lithium_type(xml_tree, api)
    elif lithium_type is None:
        children = xml_tree.getchildren()
        if not children:
            return []
        if 'name' in children[0].attrib:
            result = {}
            for child in xml_tree.getchildren():
                result[child.get('name')] = xml_to_type(child, api)
        else:
            result = []
            for child in xml_tree.getchildren():
                result.append(xml_to_type(child, api))
        return result
    else:
        return primitive_type(xml_tree)

types_map = {
    'category': Category,
    'board': Board,
    'blog': Blog,
    'user': User,
    'message': Message,
    'message_status': MessageStatus,
    'label': Label,

    'event_subscription_manager': EventSubscriptionManager,
    'event_subscription': EventSubscription,

    'value': primitive_type,
}
