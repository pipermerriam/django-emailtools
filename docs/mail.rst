Email
=====
Markdown-templated email.

An email template looks like this:

::

    ---
    subject: Hello, {{user.first_name}}
    ---
    Welcome to the site.

When using :func:`send_markdown_mail`, its output is placed in a layout to
produce a full html document::
::

    <!DOCTYPE html>
    <html>
        <body>
            {{content}}
        </body>
    </html>

The default layout is specified in ``settings.EMAIL_LAYOUT``, but can be
overridden on a per-email basis.

.. automodule:: emailtools.mail
.. autofunction:: emailtools.mail.create_markdown_mail
.. autofunction:: emailtools.mail.send_markdown_mail
.. autofunction:: emailtools.mail.render_template
.. autofunction:: emailtools.mail.extract_frontmatter
