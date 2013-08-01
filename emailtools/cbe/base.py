from functools import update_wrapper

from django.utils.decorators import classonlymethod
from django.core.exceptions import ImproperlyConfigured


class BaseEmail(object):
    """
    Simple base class for all class-based emails.  Implements the basic
    structure for constructing an email message and sending it, along with the
    `as_callable` method logic.
    """
    @property
    def email_message_class(self):
        raise ImproperlyConfigured('No `email_message_class` provided')

    @email_message_class.setter  # NOQA
    def email_message_class(self, value):
        self.__dict__['email_message_class'] = value
        return value

    def get_email_message_kwargs(self, **kwargs):
        return kwargs

    def get_email_message_class(self):
        return self.email_message_class

    def get_email_message(self):
        return self.get_email_message_class()(**self.get_email_message_kwargs())

    def get_send_kwargs(self, **kwargs):
        return kwargs

    def send(self):
        self.get_email_message().send(**self.get_send_kwargs())

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @classonlymethod
    def as_callable(cls, **initkwargs):
        for key in initkwargs:
            if not hasattr(cls, key):
                raise TypeError("{0}() received an invalid keyword {1!r}. "
                                "as_callable only accepts arguments that are "
                                "already attributes of the "
                                "class.".format(cls.__name__, key))

        EmailClass = type("Callable{0}".format(cls.__name__), (cls,), initkwargs)

        def callable(*args, **kwargs):
            self = EmailClass(*args, **kwargs)
            return self.send()

        update_wrapper(callable, EmailClass, updated=())
        return callable
