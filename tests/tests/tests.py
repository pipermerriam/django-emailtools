from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from emailtools import BasicEmail, HTMLEmail, MarkdownEmail


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
        email_callable = self.TestEmail.as_callable()
        message = email_callable.message()

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

    def test_to_address_as_string(self):
        self.create_and_send_a_message(to='string@example.com')
        message = mail.outbox[0]
        self.assertEqual(message.to, ['string@example.com'])

    def test_missing_to(self):
        self


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

    def test_template_used(self):
        with self.assertTemplateUsed(template_name=self.EMAIL_ATTRS['template_name']):
            self.create_and_send_a_message()

    def test_html_body(self):
        self.create_and_send_a_message()
        message = mail.outbox[0]
        html_body = message.alternatives[0][0]
        self.assertInHTML('<h1>test title</h1>', html_body)
        self.assertInHTML('<p>test content</p>', html_body)

    def test_plain_body(self):
        self.create_and_send_a_message()
        message = mail.outbox[0]
        self.assertIn('test title', message.body)
        self.assertIn('test content', message.body)
        self.assertNotIn('<h1>', message.body)
        self.assertNotIn('<p>', message.body)


@override_settings(EMAIL_LAYOUT='mail/base.html')
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
