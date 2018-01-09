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
    imap_hostname = imap.server.tld
    imap_ssl = True
    imap_port = 143
    """

    def is_authenticated(self, user, password):
        hostname = ""
        if self.configuration.has_option("auth", "imap_hostname"):
            hostname = self.configuration.get("auth", "imap_hostname")
        secure = True
        if self.configuration.has_option("auth", "imap_ssl"):
            secure = self.configuration.getboolean("auth", "imap_ssl")
        port = imaplib.IMAP4_SSL_PORT
        if self.configuration.has_option("auth", "imap_port"):
            port = self.configuration.get("auth", "imap_port") #TODO: cast port to int with proper error handling

        if sys.version_info < (3, 4) and secure:
            raise RuntimeError("Secure IMAP is not availabe in Python < 3.4")
        try:
            connection = imaplib.IMAP4(host=hostname, port=port)
            try:
                if sys.version_info < (3, 4):
                    connection.starttls()
                else:
                    connection.starttls(ssl.create_default_context())
            except (imaplib.IMAP4.error, ssl.CertificateError) as e:
                if secure:
                    raise
                self.logger.debug("Failed to establish secure connection: %s",
                                  e, exc_info=True)
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
                               "%s" % (hostname, e)) from e
            # TODO: ^ find out how to add int port in log message
