"""
libpttea.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of libpttea exceptions.
"""


class LibptteaException(Exception):

    def __init__(self, message="no description"):

        super().__init__(message)


class ConnectionClosed(LibptteaException):
    """Connection is Closed"""

    def __init__(self, message=__doc__):
        self.message = message

    def __str__(self):
        return self.message


class ConnectionError(LibptteaException):
    """Connection has Error"""

    def __init__(self, message=__doc__):
        self.message = message

    def __str__(self):
        return self.message
