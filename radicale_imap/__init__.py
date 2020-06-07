# RadicaleIMAP IMAP authentication plugin for Radicale.
# Copyright (C) 2017, 2020 Unrud <unrud@outlook.com>
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
import string

from radicale.auth import BaseAuth
from radicale.log import logger


def imap_address(value):
    if "]" in value:
        pre_address, pre_address_port = value.rsplit("]", 1)
    else:
        pre_address, pre_address_port = "", value
    if ":" in pre_address_port:
        pre_address2, port = pre_address_port.rsplit(":", 1)
        address = pre_address + pre_address2
    else:
        address, port = pre_address + pre_address_port, None
    try:
        return (address.strip(string.whitespace + "[]"),
                None if port is None else int(port))
    except ValueError:
        raise ValueError("malformed IMAP address: %r" % value)


def imap_security(value):
    fields = value.split(':', 1)
    security = fields[0]
    option = len(fields) > 1 and fields[1] or ""
    if security not in ("tls", "starttls", "none"):
        raise ValueError("unsupported IMAP security: %r" % security)
    if option not in ("anycert", ""):
        raise ValueError("unsupported IMAP security option: %r" % option)
    return (security, option)


PLUGIN_CONFIG_SCHEMA = {"auth": {
    "imap_host": {"value": "", "type": imap_address},
    "imap_security": {"value": "tls", "type": imap_security}}}


class Auth(BaseAuth):
    """Authenticate user with IMAP."""

    def __init__(self, configuration):
        super().__init__(configuration.copy(PLUGIN_CONFIG_SCHEMA))

    def create_ssl_context(self, anycert):
        ssl_context = ssl.create_default_context()

        if anycert:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        return ssl_context

    def login(self, login, password):
        host, port = self.configuration.get("auth", "imap_host")
        security, option = self.configuration.get("auth", "imap_security")
        try:
            if security == "tls":
                port = 993 if port is None else port
                connection = imaplib.IMAP4_SSL(
                    host=host, port=port,
                    ssl_context=self.create_ssl_context(option == "anycert"))
            else:
                port = 143 if port is None else port
                connection = imaplib.IMAP4(host=host, port=port)
                if security == "starttls":
                    connection.starttls(self.create_ssl_context(option == "anycert"))
            try:
                connection.login(login, password)
            except imaplib.IMAP4.error as e:
                logger.debug(
                    "IMAP authentication failed: %s", e, exc_info=True)
                return ""
            connection.logout()
            return login
        except (OSError, imaplib.IMAP4.error) as e:
            raise RuntimeError("Failed to communicate with IMAP server %r: "
                               "%s" % ("[%s]:%d" % (host, port), e)) from e
