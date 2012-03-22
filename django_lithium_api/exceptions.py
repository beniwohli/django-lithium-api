# -*- coding: utf-8 -*-

class LithiumException(Exception):
    pass


class MethodNotSupported(LithiumException):
    pass


class ArgumentsMissing(LithiumException):
    pass


class UnknownResponseType(LithiumException):
    pass

class RemoteException(LithiumException):
    pass