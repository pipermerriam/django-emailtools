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
