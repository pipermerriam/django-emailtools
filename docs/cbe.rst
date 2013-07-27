Class-based emails
------------------

``django-emailtools`` takes an approach to sending emails similar to the
class-based view's approach to view callables.  At Fusionbox we've found that
our email sending often follows a predictable pattern and class-based emails
arose from that pattern.

Ultimately, the goal of class-based emails is to assist developers in following
the DRY principle and reuse code through inheritance and mixin classes.

Basic Example
~~~~~~~~~~~~~

A very basic example of sending emails in django using the built in
``send_mail`` function might look something like the following.

.. code-block:: python

    from django.core.mail import send_mail

    def send_registration_email():
        send_mail(
            'A new user has registered on example.com.',
            'A user has registered',
            'admin@example.com',
            ['webmaster@example.com'],
        )


Now, here is the same example using class based emails.

.. code-block:: python

    from emailtools.cbe import BasicEmail

    class RegisteredEmail(BasicEmail):
        to = 'webmaster@example.com'
        from_email = 'admin@example.com'
        subject = 'A user has registered'
        message = 'A new user has registered on example.com.'

   send_registration_email = UserRegisteredEmail.as_callable()

In both examples, calling the ``send_registration_email`` function will send an email to `webmaster@example.com` from the address `webmaster@example.com` with the subject *"A user has registered"* and with the message body *"A new user has registered on example.com"*.  Admittedly, this example is not very useful, so lets look at making some of these values more dynamic.


Setting dynamic values
~~~~~~~~~~~~~~~~~~~~~~

Now, lets write another example, in which our message body and the email recipient list and message body are dynamic.

.. code-block:: python

   # accounts/emails.py
   from emailtools.cbe import BasicEmail

   class WelcomeEmail(BasicEmail):
       from_email = 'admin@example.com'
       subject = 'Welcome to example.com'

       def get_to(self):
           return [self.args[0].email]

       def get_body(self):
           return """Dear {user.username},

           Welcome to example.com,

           - The example.com Team""".format(user=self.args[0])

    send_welcome_email = WelcomeEmail.as_callable()

Our new ``send_welcome_email`` function expects a single argument which it expects to be a ``user`` instance, from which it will extract the ``username`` for the message body, and the ``to`` address.  To send our email, we just call the ``send_welcome_email`` function with a user instance.

.. code-block:: python

   >>> from app.emails import send_welcome_email
   >>> user = User.objects.get(...)
   >>> send_welcome_email(user)  # Sends the welcome email.

Instead of passing all of configuration in through
:meth:`~emailtools.HTMLEmail.as_callable`, we define them as attributes on the
class.  Inside of our :meth:`~emailtools.HTMLEmail.get_to` we access
``self.args`` to get the ``to`` email address.  The 'callable` email function
returned by :meth:`~emailtools.HTMLEmail.as_callable` sets the ``args`` and
``kwargs`` on the ``self``, making them accessible from ``self.args`` and
``self.kwargs`` within your class.


HTML Emails
~~~~~~~~~~~

class-based emails provides the class :class:`~emailtools.HTMLEmail`.  Lets
improve on our previous example.  First lets make ourselves a template.::

    # some_app/templates/welcome_email.html
    <h1>Welcome to example.com</h1>
    <p>Hello {{ email }}. Thanks for signing up to <a href="http://www.example.com">example.com</a></p>

And now, we'll write our Email class.  While we're at it, lets personalize our
message a bit and include the email address in the body of the message.::

    from emailtools.cbe import HTMLEmail

    class WelcomeEmail(HTMLEmail):
        from_email = 'admin@example.com'
        subject = 'Welcome'
        body = 'Welcome to example.com'
        template_name = 'welcome_email.html'

        def get_to(self):
            return self.args[0]

        def get_context_data(self, **kwargs):
            kwargs = super(WelcomeEmail, self).get_context_data(**kwargs)
            kwargs['email'] = self.args[0]
            return kwargs

     send_welcome_email = WelcomeEmail.as_callable()
     
     # Send the email
     send_welcome_email('user@example.com')

This should be very familiar to anyone who's had any experience with class-based views.

Markdown Emails
~~~~~~~~~~~~~~~

We all know how much developers love markdown.  ``django-emailtools`` also
ships with a :class:`~emailtools.MarkdownEmail` class.

.. note::

    :class:`~emailtools.MarkdownEmail` requires a layout template.  By default,
    it will use whatever is set in ``settings.EMAIL_LAYOUT``.  This can be
    overridden on subclasses with the ``layout_template`` attribute, or
    dynamically via the :meth`~emailtools.MarkdownEmail.get_layout_template`
    method.

    This template is responsible for constructing the html that wraps around
    the body of the message content.
