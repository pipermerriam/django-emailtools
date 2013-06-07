from functools import update_wrapper

from django.utils.decorators import classonlymethod
from django.core.exceptions import ImproperlyConfigured


class BaseEmail(object):
    email_message_class = None

    def get_email_message_kwargs(self, **kwargs):
        return kwargs

    def get_email_message_class(self):
        if self.email_message_class is None:
            raise ImproperlyConfigured('No `email_message_class` provided')
        return self.email_message_class

    def get_email_message(self):
        return self.get_email_message_class()(**self.get_email_message_kwargs())

    def get_send_kwargs(self, **kwargs):
        return kwargs

    def send(self):
        self.get_email_message().send(self.get_send_kwargs())

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    @classonlymethod
    def as_callable(cls, **initkwargs):
        for key in initkwargs:
            if not hasattr(cls, key):
                raise TypeError("{0}() received an invalid keyword {1!r}. "
                                "as_callable only accepts arguments that are "
                                "already attributes of the "
                                "class.".format(cls.__name__, key))

        def callable(*args, **kwargs):
            self = cls(**initkwargs)
            self.args = args
            self.kwargs = kwargs
            return self.send()

        def message(*args, **kwargs):
            self = cls(**initkwargs)
            self.args = args
            self.kwargs = kwargs
            return self.get_email_message()

        callable.message = message

        update_wrapper(callable, cls, updated=())
        update_wrapper(callable.message, cls, updated=())
        return callable
