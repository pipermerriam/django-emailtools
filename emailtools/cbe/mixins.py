from django.template import loader
from django.core.exceptions import ImproperlyConfigured


class TemplateEmailMixin(object):
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
