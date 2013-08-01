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
        body = 'A new user has registered on example.com.'

   send_registration_email = UserRegisteredEmail.as_callable()

In both examples, calling the ``send_registration_email`` function will send an email to `webmaster@example.com` from the address `webmaster@example.com` with the subject *"A user has registered"* and with the message body *"A new user has registered on example.com"*.  Admittedly, this example is not very useful, so lets look at making some of these values more dynamic.


Emails with dynamic values
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

.. note::

   The :class:`~email.BasicEmail` class is essentially a wrapper around the
   ``django.core.email.EmailMessage`` class with both properties and method
   hooks for configuring, instantiating, and sending emails using that class.


HTML Emails
~~~~~~~~~~~

While the simple examples above may work well for simple emails, most modern
web applications are not just sending plain text emails.  ``emailtools`` ships
with two solutions for constructing and sending emails with both a plain text
message and an html message. Both the :class:`~emailtools.HTMLEmail` and
:class:`~emailtools.MarkdownEmail` classes extend
``django.core.email.EmailMultiAlternative``, and uses django's built in
template engine to set the html message on the email.

Lets rewrite the welcome email class to send an html message.

.. code-block:: python

   from emailtools import HTMLEmail

   class WelcomeEmail(HTMLEmail):
       template_name = 'app/welcome_email.html'
       from_email = 'admin@example.com'
       subject = 'Welcome to example.com'

       def get_to(self):
           return [self.args[0].email]

       def get_context_data(self, **kwargs):
           kwargs = super(WelcomeEmail, self).get_context_data(**kwargs)
           kwargs['user'] = self.args[0]
           return kwargs

    send_welcome_email = WelcomeEmail.as_callable()

And now our template.

.. code-block:: html

    # app/templates/app/welcome_email.html
    <h1>Welcome to example.com</h1>
    <p>Dear {{ user.email }}</p>
    <p>Thank you for signing up to <a href="http://www.example.com">example.com</a></p>
    <p>The example.com team</p>

Now, our message will be rendered using the template engine.

Call Signature
~~~~~~~~~~~~~~

Up until now, accessing the calling arguments for our email function has
involved accessing them in ``self.args`` or ``self.kwargs``, which is both ugly
and unintuitive.  If you take a look at the ``__init__`` method of
:class:`~emailtools.BaseEmail` you'll see that it merely sets ``*args`` and
``**kwargs`` as ``self.args`` and ``self.kwargs``.  This is the default
behavior for all email classes, and it is entirely in the developers hands to
override this in any way you please.

Here is a slighltly modified version of our ``WelcomeEmail`` that demonstrates
this concept.

.. code-block:: python

   from emailtools import HTMLEmail

   class WelcomeEmail(HTMLEmail):
       template_name = 'app/welcome_email.html'
       from_email = 'admin@example.com'
       subject = 'Welcome to example.com'

       def __init__(self, user):
           self.user = user
           self.to = [user.email]

       def get_context_data(self, **kwargs):
           kwargs = super(WelcomeEmail, self).get_context_data(**kwargs)
           kwargs['user'] = self.user
           return kwargs

    send_welcome_email = WelcomeEmail.as_callable()


We gain readability, and validation that the caller complied with the call
signature of our email class.  In this example, we didn't call super on
``__init__``, which is fine.  The ``__init__`` method is yours to overide and
modify in whatever way suites the needs of your application.

About ``as_callable(**kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At this point, if you've used class based views, you should be noticing some
similarities in ``as_callable`` and ``as_view``.  ``as_callable`` returns a
callable function that will send the email.  By default, any ``*args`` and ``kwargs``
passed into the email callable are accessible via ``self.args`` and
``self.kwargs``, similar to class based views.  This however is only the
default implimentation of the ``__init__`` method for class based emails.  You
may override the ``__init__`` method however you would like.

From our example above, the following two ways of sending emails are
effectively the same.

.. code-block:: python

   >>> from my_app.emails import WelcomeEmail
   >>> send_welcome_email = WelcomeEmail.as_callable()
   >>> send_welcome_email(user)  # Sends the email.
   >>> email_instance = WelcomeEmail(user)
   >>> email_instance.send()
   
Directly calling the email callable, and calling ``send()`` on the instantiated
email class are identical.
