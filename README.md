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

# IMAP server host name
# For example: imap.server.tld
#imap_hostname =

# IMAP port to use
# For example: 143
#imap_port = 143

# Use StartTLS to secure the connection
# Requires Python >= 3.4
#imap_ssl = True
```

## License

[GPL-3.0](https://github.com/Unrud/RadicaleIMAP/blob/master/COPYING)
