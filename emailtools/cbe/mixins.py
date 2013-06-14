from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.template import loader
from django.utils.http import int_to_base36


class TemplateEmailMixin(object):
    """
    Mixin for using template rendering for the email message body.
    """
    template_name = None

    def get_template_names(self):
        if self.template_name is None:
            raise ImproperlyConfigured('No `template_name` provided')
        return [self.template_name]

    def get_context_data(self, **kwargs):
        return kwargs

    def get_rendered_template(self):
        return loader.render_to_string(
            self.get_template_names(),
            self.get_context_data(),
        )

    def get_body(self):
        return self.get_rendered_template()


class BuildAbsoluteURIMixin(object):
    """
    Mixin which provides methods for constructing absolute uris.
    """
    protocol = 'http'

    def get_domain(self):
        return Site.objects.get_current().domain

    def get_protocol(self):
        return self.protocol

    def reverse_absolute_uri(self, view_name, args=None, kwargs=None):
        location = reverse(view_name, args=args, kwargs=kwargs)
        return self.build_absolute_uri(location)

    def build_absolute_uri(self, location):
        current_uri = '{protocol}://{domain}{location}'.format(
            protocol=self.get_protocol(),
            domain=self.get_domain(),
            location=location,
        )
        return current_uri


class UserTokenEmailMixin(BuildAbsoluteURIMixin):
    """
    Mixin which provides methods for generating token based links.
    """
    UID_KWARG = 'uidb36'
    TOKEN_KWARG = 'token'

    token_generator = default_token_generator

    def get_user(self):
        return self.args[0]

    def generate_token(self, user):
        return self.token_generator.make_token(user)

    def get_uid(self, user):
        return int_to_base36(user.pk)

    def reverse_token_url(self, view_name, args=None, kwargs={}):
        kwargs.setdefault(self.UID_KWARG, self.get_uid(self.get_user()))
        kwargs.setdefault(self.TOKEN_KWARG, self.generate_token(self.get_user()))
        return self.reverse_absolute_uri(view_name, args=args, kwargs=kwargs)
