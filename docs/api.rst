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

.. currentmodule:: emailtools.cbe.base

BasicEmail
----------

.. class:: BasicEmail

   This class is the simplest implementation for class-based emails, and can be
   thought of as a loose wrapper around ``django.core.email.EmailMessage``.
   The class provides properties and methods for declaring or building each of
   the arguments used to instantiate and send an ``EmailMessage``.

    .. attribute:: email_message_class

        * default: ``django.core.email.EmailMessage``

    .. attribute:: ``subject``

        Static property to be used as the ``subject`` attribute for the email message.

    .. attribute:: ``to``

        Static property to be used as the ``to`` address for the email message.

    .. attribute:: ``cc``

        Static property to be used as the ``cc`` attribute for the email message.

    .. attribute:: ``bcc``

        Static property to be used as the ``bcc`` attribute for the email message.

    .. attribute:: ``from_email``

        Static property to be used as the ``from_email`` attribute for the email message.

    .. attribute:: ``body``

        Static property to be used as the ``body`` attribute for the email message.

    .. attribute:: ``connection``

        Static property to be used as the ``connection`` to be used for sending
        the email message.

    .. attribute:: ``attachments``

        Static property to be used for the ``attachments`` of the email message.

    .. attribute:: ``headers``

        Static property to be used for the ``headers`` of the email message.

    .. attribute:: ``fail_silently``

        Passed to the ``send`` method of the email message, to determine
        whether exceptions raised while sending should be squashed.

    .. method:: ``get_to``

        Returns the list of email addresses the email addresses should be sent to.

    .. method:: ``get_cc``

        Returns the list of email addresses the email addresses should be cc'd.

    .. method:: ``get_bcc``

        Returns the list of email addresses the email addresses should be bcc'd.

    .. method:: ``get_from_email``

        Returns the email address the email addresses will be from.

    .. method:: ``get_body``

        Returns the message body for the email message.

    .. method:: ``get_connection``

        Returns the email connection to be used for sending the email message.

    .. method:: ``get_headers``

        Returns any headers to be added to the email message.

HTMLEmail
---------

.. class:: HTMLEmail

   This class leverages the django template engine to attach an html message to
   the email message.

    .. attribute:: email_message_class

        * default: ``django.core.email.EmailMessage``

    .. attribute:: template_name

        Path to the template that should be used for rendering the body of the message.

    .. method:: get_context_data(**kwargs)

        Constructs and returns the context to be used for template rendering.


MarkdownEmail
-------------

.. class:: MarkdownEmail

   Similar to :class:`HTMLEmail`, this class uses the django template engine for rendering an html email message.  It however expects a template written in markdown, which is then inserted into the body of a base html template.

    .. attribute:: layout_template

        Declares what template should be used as the base layout for this
        email.  This template should expect a context variable ``content``
        which will contain the rendered markdown of the message.

    .. attribute:: template_name

        Path to the template that should be used for rendering the body of the message.

    .. method:: get_context_data(**kwargs)

        Constructs and returns the context to be used for template rendering.

    .. method:: get_layout_template()

        Returns the template that should be used for rending the base html
        layout of the message.

    .. method:: get_layout_context_data(**kwargs)

        Constructs and renders the context data for the base layout template.
