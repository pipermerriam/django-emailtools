``emailtools.cbe.base``
=======================

This document provides API reference material for the classes and mixins found
in ``emailtools``.

.. currentmodule:: emailtools.cbe.base



BaseEmail
---------

.. class:: BaseEmail

   This is the base class for all class based emails.  While not usable on its
   own, it establishes the base api for email sending.

    .. attribute:: email_message_class

        The ``class`` that will be used to construct the email message.

    .. method:: get_email_message_class()

        Returns the email message class.

    .. method:: get_email_message_kwargs()

        Constructs and returns the ``kwargs`` that will be used to instantiate the email message.

    .. method:: get_email_message()

        Constructs and returns the instantiated email message.

    .. method:: get_send_kwargs(**kwargs)

        Construct and returns the ``kwargs`` that will be passed to the ``send`` method of
        the instantaited email message.

    .. method:: send()

        Constructs and sends the email message.

    .. method:: as_callable()

        Returns the email callable that can be used to send the email message,
        or construct and return the unsent email message.


BasicEmail
----------

.. class:: BasicEmail

   This class is the simplest implementation for class-based emails, and can be
   thought of as a loose wrapper around ``django.core.email.EmailMessage``.
   The class provides properties and methods for declaring or building each of
   the arguments used to instantiate and send an ``EmailMessage``.

    .. attribute:: email_message_class

        * default: ``django.core.email.EmailMessage``

    .. attribute:: ``to``

        Static property to be used as the ``to`` address for the email message.
