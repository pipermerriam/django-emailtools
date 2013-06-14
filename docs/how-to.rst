How To
------

Here we will explore some examples using class-based emails.

Sending a Welcome Email
~~~~~~~~~~~~~~~~~~~~~~~

In the introduction to class-based emails, we demonstrated some very basic
patterns for sending a welcome email.  Here, we will expand on those patterns a
bit further to demonstrate a real use case example.

Our goal here will be to send a welcome email to newly registered users by
hooking into the ``post_save`` signal provided by Django.

Password Reset Email
~~~~~~~~~~~~~~~~~~~~

Sending a password reset email manually.  First lets take a look at how Django
does this in the built in :class:`PasswordResetForm` packaged with
``django.contrib.auth``.::

    class PasswordResetForm(forms.Form):
        email = forms.EmailField(label=_("Email"), max_length=254)

        def save(self, domain_override=None,
                 subject_template_name='registration/password_reset_subject.txt',
                 email_template_name='registration/password_reset_email.html',
                 use_https=False, token_generator=default_token_generator,
                 from_email=None, request=None):
            """
            Generates a one-use only link for resetting password and sends to the
            user.
            """
            from django.core.mail import send_mail
            UserModel = get_user_model()
            email = self.cleaned_data["email"]
            users = UserModel._default_manager.filter(email__iexact=email)
            for user in users:
                # Make sure that no email is sent to a user that actually has
                # a password marked as unusable
                if user.password == UNUSABLE_PASSWORD:
                    continue
                if not domain_override:
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                else:
                    site_name = domain = domain_override
                c = {
                    'email': user.email,
                    'domain': domain,
                    'site_name': site_name,
                    'uid': int_to_base36(user.pk),
                    'user': user,
                    'token': token_generator.make_token(user),
                    'protocol': 'https' if use_https else 'http',
                }
                subject = loader.render_to_string(subject_template_name, c)
                # Email subject *must not* contain newlines
                subject = ''.join(subject.splitlines())
                email = loader.render_to_string(email_template_name, c)
                send_mail(subject, email, from_email, [user.email])

Given a valid email address, the password reset form does the following.

1.  Lookup all users with that email address, skipping users who have unusable passwords.
2.  Figure out the domain, site information, and other context data. (for constructing urls).
3.  Render the password reset template.
4.  Send the password reset email(s).

Our goal will be to reproduce this logic in a class-based view that we call
with a single argument, the email address.:

.. code-block:: python

    # accounts/emails.py
    class PasswordResetEmail(HTMLEmail):
        ...

    password_reset_email = PasswordResetEmail.as_callable()

And to use it from a view.

.. code-block:: python

    # accounts/views.py
    from accounts.emails import password_reset_email

    class PasswordResetView(FormView):
        ...
        def form_valid(self, form):
            # Send the password reset email.
            password_reset_email(form.cleaned_data['email'])
            return super(PasswordResetView, self).form_valid(form)

Now that we know what our interface should look like, lets start writing our
email class.

Step 1: Looking up Users
^^^^^^^^^^^^^^^^^^^^^^^^

First, we need a way to find all of the users who's email matches our target
email.  Since we need to send a password reset email for every user with the
target email, this logic needs to live outside of our email class.  For this
example, i'll simply make a function to wrap around our email callable.

.. code-block:: python

    # accounts/emails.py
    from django.contrib.auth import get_user_model, UNUSABLE_PASSWORD
    from emailtools import HTMLEmail

    UserModel = get_user_model()

    class PasswordResetEmail(HTMLEmail):
        from_address = 'admin@example.com'
        subject = 'Password reset on example.com'

        def get_to(self):
            return [self.args[0].email]

    send_password_reset_email = PasswordResetEmail.as_callable()

    def password_reset_email(email):
        users = UserModel._default_manager.filter(
            email__iexact=email).exclude(
            password=UNUSABLE_PASSWORD)
        for user in users:
            send_password_reset_email(user)

.. note:

    The logic to lookup and loop over the users could easily live in many
    places within your app.

    1. As a method on your User model.
    2. Inside your ``password_reset`` view.
    3. A method on the ModelAdmin class registered with your user.

    The point to take from this is that class-based emails are meant to make
    **sending** emails easy and trying to include logic that lives outside of
    the constructing and sending of an email may lead to headaches.

Step 2: Domain and Site information.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we can loop over all of the users, lets get our site and domain
information ready for template rendering.  For this, we'll want to hook into
the method call to :meth:`~emailtools.HTMLEmail.get_context_data`.:

.. code-block:: python

    # accounts/emails.py
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import int_to_base36

    from emailtools import HTMLEmail

    class PasswordResetEmail(HTMLEmail):
        token_generator = default_token_generator
        ...
        def get_context_data(self, **kwargs):
            kwargs = super(PasswordResetEmail, self).get_context_data(**kwargs)
            current_site = Site.objects.get_current()
            kwargs.update({
                'site_name': current_site.name,
                'domain': current_site.domain,
                'uid': int_to_base36(user.pk),
                'email': self.args[0].email,
                'user': self.args[0],
                'token': self.token_generator.make_token(user),
            })
            return kwargs

While this will suffice for reproducing the behavior of
:meth:`~django.contrib.auth.forms.PasswordResetForm.save`, constructing urls in
templates via string concatenation has always seemed prone to human error.
Additionally, there are so many uses for email tokens so wouldn't it be nice to
have a reusable tool for sending such emails.

First, lets write ``BuildAbsoluteURIMixin``, a mixin class for your email classes
which provides the url reversing that returns absolute urls.


.. code-block:: python

    # mixins.py
    from urlparse import urljoin

    from django.contrib.auth.tokens import default_token_generator
    from django.contrib.sites.models import Site
    from django.core.urlresolvers import reverse

    class BuildAbsoluteURIMixin(object):
        use_https = False

        def get_site(self):
            return get_current_site(request)

        def reverse_absolute_uri(self, *args, **kwargs):
            current_site = Site.objects.get_current()
            location = reverse(*args, **kwargs)
            current_uri = '{protocol}://{domain}{location}'.format(
                protocol=('https' if self.use_https else 'http'),
                domain=current_site.domain,
                location=location,
            )
            return urljoin(current_uri, location)

Now, lets write a ``UserTokenEmailMixin`` which will provide user based
token generation for our emails.

.. code-block:: python

    # mixins.py
    class UserTokenEmailMixin(object):
        token_generator = default_token_generator
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import int_to_base36

        def generate_token(self, user):
            return self.token_generator.make_token(user)

        def get_uid(self, user):
            return int_to_base36(self, user):

Now, lets rewrite ``PasswordResetEmail`` to make use of these two new mixins.

.. code-block:: python

    # accounts/emails.py
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import int_to_base36

    from emailtools import HTMLEmail

    from mixins import UserTokenEmailMixin, BuildAbsoluteURIMixin

    class PasswordResetEmail(UserTokenEmailMixin, BuildAbsoluteURIMixin, HTMLEmail):
        ...
        def get_context_data(self, **kwargs):
            kwargs = super(PasswordResetEmail, self).get_context_data(**kwargs)
            current_site = self.get_site()
            user = self.args[0]
            kwargs.update({
                'site_name': current_site.name,
                'domain': current_site.domain,
                'email': self.args[0].email,
                'user': self.args[0],
                'password_reset_complete_uri': self.reverse_absolute_uri(
                    'password_reset_complete',
                    kwargs={'uidb36': self.get_uid(user), 'token': self.generate_token(user)},
                ),
            })
            return kwargs
