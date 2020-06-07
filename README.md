# Radicale IMAP

IMAP authentication plugin for [Radicale](http://radicale.org/).

## Installation

```shell
$ python3 -m pip install --upgrade git+https://github.com/Unrud/RadicaleIMAP
```

## Configuration

```ini
[auth]
type = radicale_imap

# IMAP server hostname
# Syntax: address
# Syntax: address:port
# Syntax: [address]:port
# For example: imap.server.tld
#imap_host =

# Secure the IMAP connection
# Value: tls | tls:anycert | starttls | starttls:anycert | none
#imap_security = tls
```

## License

[GPL-3.0](https://github.com/Unrud/RadicaleIMAP/blob/master/COPYING)
