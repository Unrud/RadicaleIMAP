import unittest
import radicale_imap
import radicale.config

# auth imap login should raise a runtime error
# and it means that the plugin tries to log the user
# against a non existent imap server which is great.
#
# this attribute is an alias for test readability
# without rewriting the whole plugin with mockability
TestIMAPSuccess = RuntimeError

class TestRadicaleImap(unittest.TestCase):
    def test_email_domain(self):
        with self.assertRaises(ValueError):
            radicale_imap.email_domain("invalid")

        with self.assertRaises(ValueError):
            radicale_imap.email_domain("invalid@domain@something")

        self.assertEqual(radicale_imap.email_domain("valid@domain"), "domain")
        self.assertEqual(
            radicale_imap.email_domain("super.valid@domain.com"), "domain.com"
        )

    def test_auth_login(self):
        auth = radicale_imap.Auth(radicale.config.load())
        auth.configuration.update(
            config={
                "auth": {
                    "allowed_domains": "test1.com, test2.com",
                    "imap_host": "127.0.0.1:0000",
                    "imap_security": "none",
                }
            }
        )
        with self.assertRaises(ValueError):
            auth.login("invalid", "p@ssw0rd")

        with self.assertRaises(TestIMAPSuccess):
            auth.login("authorized@test1.com", "p@ssw0rd")

        with self.assertRaises(TestIMAPSuccess):
            auth.login("authorized@test2.com", "p@ssw0rd")

        # example.com is not an authorized domain
        self.assertEqual(auth.login("unauthorized.domain@example.com", "p@ssw0rd"), "")

        # test with empty allowed_domains
        auth = radicale_imap.Auth(radicale.config.load())
        auth.configuration.update(
            config={
                "auth": {
                    "imap_host": "127.0.0.1:0000",
                    "imap_security": "none",
                }
            }
        )
        with self.assertRaises(TestIMAPSuccess):
            auth.login("authorized@test1.com", "p@ssw0rd")

        auth.configuration.update(
            config={
                "auth": {
                    "allowed_domains": "",
                    "imap_host": "127.0.0.1:0000",
                    "imap_security": "none",
                }
            }
        )
        with self.assertRaises(TestIMAPSuccess):
            auth.login("authorized@test1.com", "p@ssw0rd")
