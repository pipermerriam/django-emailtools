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
``send_mail`` function might look something like the following.::

    from django.core.mail import send_mail

    def send_welcome_email():
        send_mail(
            'Welcome',
            'Welcome to example.com',
            'admin@example.com',
            ['user@example.com'],
        )


Using class-based emails::

    from emailtools.cbe import BasicEmail

    send_welcome_email = BasicEmail.as_callable(
        to='user@example.com',
        from_email='admin@example.com',
        subject='Welcome',
        body='Welcome to example.com',
    )

In both examples, calling the ``send_welcome_email`` function will send our
welcome email to ``user@example.com``.  Since we only wanted to set a few
attributes, we pass these into the :meth`~BaseEmail.as_callable` method
itself.


A More Useful Example
~~~~~~~~~~~~~~~~~~~~~

Our basic example isn't actually that useful.  Lets modify it a bit to allow us
to dynamically set the ``to`` address on the email.  To do this, we will
subclass :class:`~emailtools.BasicEmail` and override the method
:meth`get_to` which is responsible for setting the ``to`` address.::

    from emailtools.cbe import BasicEmail

    class WelcomeEmail(BasicEmail):
        from_email = 'admin@example.com'
        subject = 'Welcome'
        body = 'Welcome to example.com'

        def get_to(self):
            return self.args[0]

     send_welcome_email = WelcomeEmail.as_callable()

     # Send the email
     send_welcome_email('user@example.com')

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
