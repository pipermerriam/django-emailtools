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
``django.contrib.auth``.:

.. code-block:: python
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
2.  Figure out the domain, site information, and other context data.
3.  Render the password reset template.
4.  Send the password reset email(s).

Our goal will be to reproduce this logic while leveraging the power of
class-based views.:

.. code-block:: python

    # accounts/emails.py
    class PasswordResetEmail(HTMLEmail):
        ...

    send_password_reset_email = PasswordResetEmail.as_callable()

And to use it from a view.

.. code-block:: python

    # accounts/views.py
    from accounts.emails import send_password_reset_email

    class PasswordResetView(FormView):
        ...
        def form_valid(self, form):
            # Send the password reset email.
            email = form.cleaned_data['email']
            users = UserModel._default_manager.filter(email__iexact=email)
            for user in users:
                password_reset_email(user)
            return super(PasswordResetView, self).form_valid(form)

Now that we know what our interface should look like, lets start writing our
email class.

Step 1: Writing the basic view
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
        template_name = 'registration/password_reset_email.html'

        def get_to(self):
            return [self.args[0].email]

    send_password_reset_email = PasswordResetEmail.as_callable()


Step 2: Domain and Site information.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now lets get our site and domain information, along with the other context
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


Step 3: Refactoring out the Re-usable components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, lets write ``BuildAbsoluteURIMixin``, a mixin class for your email classes
which provides the url reversing that returns absolute urls.


.. code-block:: python

    # mixins.py
    from django.contrib.auth.tokens import default_token_generator
    from django.contrib.sites.models import Site
    from django.core.urlresolvers import reverse

    class BuildAbsoluteURIMixin(object):
        protocol = 'http'

        def get_domain(self):
            return Site.objects.get_current().domain

        def get_protocol(self):
            return self.protocol

        def reverse_absolute_uri(self, view_name, args=None, kwargs=None):
            location = reverse(view_name, args=args, kwargs=kwargs)
            return self.build_absolute_uri(location)

        def build_absolute_uri(self, location):
            return '{protocol}://{domain}{location}'.format(
                protocol=self.get_protocol(),
                domain=self.get_domain(),
                location=location,
            )


Now, lets write a ``UserTokenEmailMixin`` which will provide user based
token generation for our emails.

.. code-block:: python

    # mixins.py
    from django.utils.http import int_to_base36

    class UserTokenEmailMixin(BuildAbsoluteURIMixin):
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

Step 4: Bringing it all together
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, lets rewrite ``PasswordResetEmail`` to make use of these new mixins.

.. code-block:: python

    # accounts/emails.py
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import int_to_base36

    from emailtools import HTMLEmail

    from mixins import UserTokenEmailMixin

    class PasswordResetEmail(UserTokenEmailMixin, MarkdownEmail):
        from_email = 'admin@example.com'
        template_name = 'registration/password_reset_email.html'
        subject = "Password Reset"
    
        def get_to(self):
            return [self.get_user().email]
    
        def get_context_data(self, **kwargs):
            kwargs = super(PasswordResetEmail, self).get_context_data()
            user = self.get_user()
            kwargs.update({
                'user': user,
                'reset_url': self.reverse_token_url('password_reset_confirm'),
            })
            return kwargs

    send_password_reset_email = PasswordResetEmail.as_callable()

Step 5: Re-usability
^^^^^^^^^^^^^^^^^^^^

A simple pattern for requiring email verification is to remove the password
fields from the signup form and send an email verification link on account
creation.  This has the pleasant side effect of simplifying the signup process
while verifying your user's email addresses.

Class based emails really shine here.  Lets look at what it would take to use
our :class:`~PasswordResetEmail` class to send a welcome email.


.. code-block:: python

    # accounts/emails.py
    send_welcome_email = PasswordResetEmail.as_callable(
        subject='Welcome to example.com'
        template_name='registration/welcome_email.html',
    )

The two mixins found in this example are also available in email tools.
