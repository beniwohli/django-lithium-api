# -*- coding: utf-8 -*-

class LithiumException(Exception):
    pass


class AuthenticationError(LithiumException):
    pass


class MethodNotSupported(LithiumException):
    pass


class ArgumentsMissing(LithiumException):
    pass


class UnknownResponseType(LithiumException):
    pass

class RemoteException(LithiumException):
    def __init__(self, message, code=None, xml_response=None):
        if code:
            message = 'Error %s: %s' % (unicode(code), message)
        super(RemoteException, self).__init__(message)
        self.code = code
        self.xml_response = xml_response