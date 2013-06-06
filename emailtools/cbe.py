from functools import update_wrapper
import markdown

from django.template import loader
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.utils.decorators import classonlymethod
from django.utils.html import strip_tags
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe


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


class BasicEmail(BaseEmail):
    email_message_class = EmailMessage
    subject = None
    to = None
    cc = None
    bcc = None
    from_email = None
    body = None
    connection = None
    attachments = None
    headers = None
    fail_silently = False

    def get_email_message_kwargs(self, **kwargs):
        kwargs = super(BasicEmail, self).get_email_message_kwargs()
        kwargs.update({
            'subject': self.get_subject(),
            'body': self.get_body(),
            'from_email': self.get_from_email(),
            'to': self.get_to(),
            'cc': self.get_cc(),
            'bcc': self.get_bcc(),
            'connection': self.get_connection(),
        })
        return kwargs

    def get_to(self):
        if self.to is None:
            raise ImproperlyConfigured('No `to` provided')
        if isinstance(self.to, basestring):
            return [self.to]
        return self.to

    def get_cc(self):
        return self.cc or tuple()

    def get_bcc(self):
        return self.bcc or tuple()

    def get_attachments(self):
        return self.attachments or tuple()

    def get_headers(self):
        return self.headers or {}

    def get_fail_silently(self):
        return self.fail_silently

    def get_send_kwargs(self, **kwargs):
        kwargs = super(BasicEmail, self).get_send_kwargs(**kwargs)
        kwargs['fail_silently'] = self.get_fail_silently()
        return kwargs

    def get_from_email(self):
        if self.from_email is None:
            raise ImproperlyConfigured('No `from_email` provided')
        return self.from_email

    def get_subject(self):
        if self.subject is None:
            raise ImproperlyConfigured('No `subject` provided')
        return self.subject

    def get_body(self):
        if self.body is None:
            raise ImproperlyConfigured('No `body` provided')
        return self.body

    def get_connection(self):
        return self.connection


class BaseHTMLEmail(BasicEmail):
    email_message_class = EmailMultiAlternatives

    def get_email_message(self):
        message = super(BaseHTMLEmail, self).get_email_message()
        message.attach_alternative(self.get_html_body(), "text/html")
        return message

    def get_html_body(self):
        return self.get_body()


class TemplateEmailMixin(object):
    template_name = None

    def get_template_names(self):
        if self.template_name is None:
            raise ImproperlyConfigured('No `template_name` provided')
        return [self.template_name]

    def get_html_body(self):
        return loader.render_to_string(
            self.get_template_names(),
            self.get_context_data(),
        )

    def get_context_data(self, **kwargs):
        return kwargs

    def get_body(self):
        return strip_tags(self.get_html_body())


class HTMLEmail(TemplateEmailMixin, BaseHTMLEmail):
    pass


class MarkdownEmail(HTMLEmail):
    layout_template = None
    template_name = None

    def get_layout_template(self):
        if self.layout_template is None:
            if getattr(settings, 'EMAIL_LAYOUT', None) is not None:
                return settings.EMAIL_LAYOUT
            raise ValueError('layout was not defined by settings.EMAIL_LAYOUT and none was provided')
        return [self.layout_template]

    def get_body(self):
        return loader.render_to_string(
            self.get_template_names(),
            self.get_context_data(),
        )

    def get_html_body(self):
        return loader.render_to_string(
            self.get_layout_template(),
            {'content': mark_safe(markdown.markdown(self.get_body(), ['extra']))},
        )
