import django
from django.core import mail
from django.test import TestCase
try:
    try:
        from django.utils import unittest
    except PendingDeprecationWarning:
        import unittest
except ImportError:
    import unittest  # NOQA
try:
    from django.test.utils import override_settings
except ImportError:
    def override_settings(*args, **kwargs):
        return unittest.skipIf(django.get_version().startswith('1.3'), "Django < 1.4 doesn't have override_settings")
from django.core.exceptions import ImproperlyConfigured


from emailtools import BaseEmail, BasicEmail, HTMLEmail, MarkdownEmail


class TestBasicCBE(TestCase):
    EMAIL_ATTRS = {
        'subject': 'test email',
        'to': ['to@example.com'],
        'from_email': 'from@example.com',
        'body': 'This is a test email',
    }

    def setUp(self):
        class TestEmail(BasicEmail):
            subject = self.EMAIL_ATTRS['subject']
            to = self.EMAIL_ATTRS['to']
            from_email = self.EMAIL_ATTRS['from_email']
            body = self.EMAIL_ATTRS['body']
        self.TestEmail = TestEmail

    def create_and_send_a_message(self, **kwargs):
        email_callable = self.TestEmail.as_callable(**kwargs)
        email_callable()

    def test_mail_is_sent(self):
        self.create_and_send_a_message()
        self.assertEqual(len(mail.outbox), 1)

    def test_create_message(self):
        email_instance = self.TestEmail()
        message = email_instance.get_email_message()

        self.assertTrue(isinstance(message, self.TestEmail.email_message_class))

    def test_to(self):
        self.create_and_send_a_message()
        message = mail.outbox[0]
        for k, v in self.EMAIL_ATTRS.iteritems():
            self.assertEqual(getattr(message, k), v)
        self.assertEqual(message.bcc, [])
        self.assertEqual(message.cc, [])

    def test_settings_override(self):
        self.create_and_send_a_message(
            to=['overridden_to@example.com'],
            cc=['overridden_cc@example.com'],
            bcc=['overridden_bcc@example.com'],
            subject='overridden_subject',
        )
        message = mail.outbox[0]
        self.assertEqual(message.to, ['overridden_to@example.com'])
        self.assertEqual(message.cc, ['overridden_cc@example.com'])
        self.assertEqual(message.bcc, ['overridden_bcc@example.com'])
        self.assertEqual(message.subject, 'overridden_subject')

    def test_improper_settings_override(self):
        with self.assertRaises(TypeError):
            self.create_and_send_a_message(not_a_class_property=True)

    def test_to_address_as_string(self):
        self.create_and_send_a_message(to='string@example.com')
        message = mail.outbox[0]
        self.assertEqual(message.to, ['string@example.com'])

    def test_missing_message_class(self):
        class TestEmail(BaseEmail):
            subject = self.EMAIL_ATTRS['subject']
            to = self.EMAIL_ATTRS['to']
            from_email = self.EMAIL_ATTRS['from_email']
            body = self.EMAIL_ATTRS['body']

        with self.assertRaises(ImproperlyConfigured):
            TestEmail.as_callable()()

    def test_missing_to(self):
        with self.assertRaises(ImproperlyConfigured):
            self.create_and_send_a_message(to=None)()

    def test_missing_from(self):
        with self.assertRaises(ImproperlyConfigured):
            self.create_and_send_a_message(from_email=None)()

    def test_missing_subject(self):
        with self.assertRaises(ImproperlyConfigured):
            self.create_and_send_a_message(subject=None)()

    def test_missing_body(self):
        with self.assertRaises(ImproperlyConfigured):
            self.create_and_send_a_message(body=None)()

    @unittest.expectedFailure
    def test_sending_kwargs(self):
        class SendingKwargsEmail(self.TestEmail):
            from_email = 'with\nnewline@gmail.com'
            fail_silently = True

        SendingKwargsEmail.as_callable(fail_silently=True)()
        with self.assertRaises(mail.BadHeaderError):
            SendingKwargsEmail.as_callable()()

    def test_basic_init_overide(self):
        class TestEmail(self.TestEmail):
            def __init__(self, x):
                super(TestEmail, self).__init__(x)

        TestEmail('arst')
        TestEmail(x='arst')

        with self.assertRaises(TypeError):
            TestEmail()

        with self.assertRaises(TypeError):
            TestEmail('arst', 'tsra')


class TestHTMLEmail(TestCase):
    EMAIL_ATTRS = {
        'subject': 'test email',
        'to': ['to@example.com'],
        'from_email': 'from@example.com',
        'template_name': 'tests/test_HTMLEmail_template.html',
    }

    def setUp(self):
        class TestHTMLEmail(HTMLEmail):
            subject = self.EMAIL_ATTRS['subject']
            to = self.EMAIL_ATTRS['to']
            from_email = self.EMAIL_ATTRS['from_email']
            template_name = self.EMAIL_ATTRS['template_name']

            def get_context_data(self, **kwargs):
                kwargs = super(TestHTMLEmail, self).get_context_data(**kwargs)
                kwargs.update({
                    'title': 'test title',
                    'content': 'test content',
                })
                return kwargs

        self.TestHTMLEmail = TestHTMLEmail

    def create_and_send_a_message(self, **kwargs):
        email_callable = self.TestHTMLEmail.as_callable(**kwargs)
        email_callable()

    def test_mail_is_sent(self):
        self.create_and_send_a_message()
        self.assertEqual(len(mail.outbox), 1)

    def test_mail_has_html_body(self):
        self.create_and_send_a_message()
        message = mail.outbox[0]
        self.assertTrue(message.alternatives)
        self.assertEqual(message.alternatives[0][1], 'text/html')

    @unittest.skipIf(django.get_version().startswith('1.3'), "Django < 1.4 doesn't allow assertTemplateUsed as a context manager")
    def test_template_used(self):
        with self.assertTemplateUsed(template_name=self.EMAIL_ATTRS['template_name']):
            self.create_and_send_a_message()

    def test_html_body(self):
        self.create_and_send_a_message()
        message = mail.outbox[0]
        html_body = message.alternatives[0][0]
        try:
            self.assertInHTML('<h1>test title</h1>', html_body)
            self.assertInHTML('<p>test content</p>', html_body)
        except AttributeError:  # support for < django 1.5
            self.assertIn('<h1>test title</h1>', html_body)
            self.assertIn('<p>test content</p>', html_body)

    def test_plain_body(self):
        self.create_and_send_a_message()
        message = mail.outbox[0]
        self.assertIn('test title', message.body)
        self.assertIn('test content', message.body)
        self.assertNotIn('<h1>', message.body)
        self.assertNotIn('<p>', message.body)


class TestMarkdownEmail(TestHTMLEmail):
    EMAIL_ATTRS = {
        'subject': 'test email',
        'to': ['to@example.com'],
        'from_email': 'from@example.com',
        'template_name': 'tests/test_MarkdownEmail_template.md',
    }

    def setUp(self):
        class TestMarkdownEmail(MarkdownEmail):
            layout_template = 'mail/base.html'
            subject = self.EMAIL_ATTRS['subject']
            to = self.EMAIL_ATTRS['to']
            from_email = self.EMAIL_ATTRS['from_email']
            template_name = self.EMAIL_ATTRS['template_name']

            def get_context_data(self, **kwargs):
                kwargs = super(TestMarkdownEmail, self).get_context_data(**kwargs)
                kwargs.update({
                    'title': 'test title',
                    'content': 'test content',
                })
                return kwargs

        self.TestMarkdownEmail = TestMarkdownEmail

    def create_and_send_a_message(self, **kwargs):
        email_callable = self.TestMarkdownEmail.as_callable(**kwargs)
        email_callable()

    @override_settings(EMAIL_LAYOUT=None)
    def test_missing_base_layout(self):
        self.create_and_send_a_message()
        with self.assertRaises(ImproperlyConfigured):
            self.create_and_send_a_message(layout_template=None)
