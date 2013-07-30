Introduction
============

``django-emailtools`` takes an approach to sending emails similar to the
class-based view's approach to view callables.  At Fusionbox we've found that
our email sending often follows a predictable pattern and class-based emails
arose from that pattern.

Ultimately, the goal of class-based emails is to 

Installation
------------

1.  Install the package::

        $ pip install django-emailtools

    Or you can install it from source::

        $ pip install -e git://github.com/fusionbox/django-emailtools@master#egg=django-emailtools-dev

2.  Add ``emailtools`` to your ``INSTALLED_APPS``.


Quick Start
===========

Write your email class and instantiate your email callable.

.. code-block:: python

   # app/emails.py
   from emailtools import BasicEmail

   class WelcomeEmail(BasicEmail):
        from_email = 'admin@example.com'
        subject = 'Welcome to example.com'
        template_name = 'welcome_email.html'

        def get_to(self):
            return [self.args[0]]

        def get_context_data(self, **kwargs):
            kwargs = super(WelcomeEmail, self).get_context_data(**kwargs)
            kwargs['email_address'] = self.args[0]
            return kwargs

   send_welcome_email = WelcomeEmail.as_callable()

Write you email template.

.. code-block:: html

   # app/templates/welcome_email.html

   <html>
        <body>
            <h1>Welcome to example.com</h2>
            <p>Here is some content about how happy we are to have you at
            example.com.  You can now login using '{{ email_address }}' as your
            username</p>
        </body>
   </html>

And to send the email.

.. code-block:: python

   >>> from app.emails import send_welcome_email
   >>> send_welcome_email('joe.smith@example.com')  # Sends the email

Or if you wanted to do something with the message before you sent it:


.. code-block:: python

   >>> from myapp.emails import WelcomeEmail
   >>> email_instance = WelcomeEmail
   >>> message = email_instance.get_email_message()
   >>> message
   <django.core.mail.message.EmailMultiAlternatives at 0x10668d150>
   >>> message.send()  # Sends the email.
