``emailtools.cbe.base``
=======================

This document provides API reference material for the classes and mixins found
in ``emailtools``.

.. currentmodule:: emailtools.cbe.base

BaseEmail
=========

.. class:: BaseEmail

    :class:`~emailtools.cbe.base.BaseEmail` objects have the following
    attributes:

    .. attribute:: email_message_class

        Required. 30 characters or fewer. Usernames may contain alphanumeric,
        ``_``, ``@``, ``+``, ``.`` and ``-`` characters.
        Determines the 

.. class:: BaseEmail

    .. method:: as_callable()

        Returns an email callable.  Calling this function will construct an
        email message of type ``email_message_class`` and send the message.
        This callable function also has a :meth:`~callable.message` method
        attached to it which returns the email message unsent.
