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
2.  Figure out the domain and other site information (for constructing urls).
3.  Render the password reset template.
4.  Send the password reset email(s).

Our goal will be to reproduce this logic in a class-based view that we call
with a single argument, the email address.::

    # accounts/emails.py
    class PasswordResetEmail(HTMLEmail):
        ...

    password_reset_email = PasswordResetEmail.as_callable()

And to use it from a view.::

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

First, we need an email class with the basic subject and sender information,
and write a way to find all of the users who's email matches our target
email.::

    # accounts.emails.py
    from django.contrib.auth import get_user_model, UNUSABLE_PASSWORD
    from emailtools import HTMLEmail

    UserModel = get_user_model()

    class PasswordResetEmail(HTMLEmail):
        from_address = 'admin@example.com'
        subject = 'Password reset on example.com'

        def get_users(self):
            return UserModel._default_manager.filter(
                email__iexact=self.args[0]).exclude(
                password=UNUSABLE_PASSWORD)

        def get_to(self):
            

TODO, no way to send multiple emails yet with CBE.
