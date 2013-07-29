import markdown

from django.template import loader
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

from .base import BaseEmail
from .mixins import TemplateEmailMixin


class BasicEmail(BaseEmail):
    """
    Class-based email based around `django.core.email.EmailMessage`
    """
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
        kwargs = super(BasicEmail, self).get_email_message_kwargs(**kwargs)
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
        kwargs.setdefault('fail_silently', self.get_fail_silently())
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


class HTMLEmail(TemplateEmailMixin, BasicEmail):
    """
    Sends an HTML email.
    """
    email_message_class = EmailMultiAlternatives

    def get_email_message(self):
        message = super(HTMLEmail, self).get_email_message()
        message.attach_alternative(self.get_rendered_template(), "text/html")
        return message

    def get_body(self):
        return strip_tags(super(HTMLEmail, self).get_body())


class MarkdownEmail(HTMLEmail):
    """
    Renders a markdown template into an HTML email.
    """
    layout_template = None
    template_name = None

    def get_layout_template(self):
        if self.layout_template is None:
            if getattr(settings, 'EMAIL_LAYOUT', None) is not None:
                return settings.EMAIL_LAYOUT
            raise ImproperlyConfigured('layout was not defined by settings.EMAIL_LAYOUT and none was provided')
        return [self.layout_template]

    def get_layout_context_data(self, **kwargs):
        return kwargs

    def get_rendered_template(self):
        md = super(MarkdownEmail, self).get_rendered_template()
        return loader.render_to_string(
            self.get_layout_template(),
            self.get_layout_context_data(content=mark_safe(markdown.markdown(md, ['extra']))),
        )
