# RadicaleIMAP IMAP authentication plugin for Radicale.
# Copyright (C) 2017 Unrud <unrud@openaliasbox.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import imaplib
import ssl
import sys

from radicale.auth import BaseAuth

VERSION = "2.0.0"


class Auth(BaseAuth):
    """Authenticate user with IMAP.

    Configuration:

    [auth]
    type = radicale_imap
    imap_host = imap.server.tld
    imap_secure = True
    imaps = True # for "old"-style imap over tls

    """

    def get_connection(self, host, port, secure, imaps):
        ssl_context = ssl.create_default_context()
        try:
            if secure and imaps:
                connection = imaplib.IMAP4_SSL(
                        host=host, port=port, ssl_context=ssl_context)
            elif secure:
                connection = imaplib.IMAP4(host=host, port=port)
                if sys.version_info < (3, 4):
                    connection.starttls()
                else:
                    connection.starttls(ssl_context)
            else:
                connection = imaplib.IMAP4(host=host, port=port)
        except (imaplib.IMAP4.error, ssl.CertificateError) as e:
            self.logger.debug("Failed to establish connection: %s",
                              e, exc_info=True)
            raise
        return connection

    def is_authenticated(self, user, password):
        host = ""
        if self.configuration.has_option("auth", "imap_host"):
            host = self.configuration.get("auth", "imap_host")
        secure = True
        if self.configuration.has_option("auth", "imap_secure"):
            secure = self.configuration.getboolean("auth", "imap_secure")
        imaps = False
        if self.configuration.has_option("auth", "imaps"):
            imaps = self.configuration.getboolean("auth", "imaps")
        try:
            if ":" in host:
                address, port = host.rsplit(":", maxsplit=1)
            else:
                address, port = host, 143
            address, port = address.strip("[] "), int(port)
        except ValueError as e:
            raise RuntimeError(
                "Failed to parse address %r: %s" % (host, e)) from e
        if sys.version_info < (3, 4) and secure:
            raise RuntimeError("Secure IMAP is not availabe in Python < 3.4")
        try:
            connection = get_connection(host, port, secure, imaps)
            try:
                connection.login(user, password)
            except imaplib.IMAP4.error as e:
                self.logger.debug(
                    "IMAP authentication failed: %s", e, exc_info=True)
                return False
            connection.logout()
            return True
        except (OSError, imaplib.IMAP4.error) as e:
            raise RuntimeError("Failed to communicate with IMAP server %r: "
                               "%s" % (host, e)) from e
