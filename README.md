
# get bitshares price

![](https://bitsharestalk.org/BitSharesFinalTM200.png)

This project provides a bitshares price feed for witnesses

# Project Setup

## Quick Start

Install
```
$ git clone https://github.com/pch957/btsprice.git
$ cd btsprice
$ python3 ./setup.py install --user
$ cp ./config.json.sample ./config.json
$ vim ./config.json
```

Set CLI Wallet object:

- witness = your witness account name
- host = localhost (if installing pricefeed on same server as the node)
- port - whatever port the cli rpc port is on (number, no quotes)
- user = leave blank
- passwd = leave blank
- unlock = the cli wallet password

```
    "witness": "",

    "cli_wallet": {
        "host" : "localhost",
        "port" : 8093,
        "user" : "",
        "passwd" : "",
        "unlock" : ""
```

Login to your cli_wallet

```
>>> import_key "your_witness_account_name" YOUR_ACTIVE_PRIVATE_KEY
```

Make sure your cli_wallet is advertising on rpc port entered in cli_wallet object above.

>Make sure this continues to run as a background process even after you logout.

```
cli_wallet -H 127.0.0.1:8093
```

Run the price feed script

>Make sure this continues to run as a background process even after you logout.

```
cd btsprice
python3 ./main.py --config ../config.json
```

Supported Python Versions
=========================

supports the following versions out of the box:

* CPython 2.6, 2.7, 3.3
* PyPy 1.9

CPython 3.0-3.2 may also work but are at this point unsupported. PyPy 2.0.2 is known to work but is not run on Travis-CI.

Jython_ and IronPython_ may also work, but have not been tested. If there is interest in support for these alternative implementations, please open a feature request!

.. _Jython: http://jython.org/
.. _IronPython: http://ironpython.net/

Licenses
========
The code which makes up this project is licensed under the MIT/X11 license. Feel free to use it in your free software/open-source or proprietary projects.

Issues
======

Please report any bugs or requests that you have using the GitHub issue tracker!

Authors
=======

* Alt
