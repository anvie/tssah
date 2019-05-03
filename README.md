TO SSH AH (TSSAH)
====================

Painless simple SSH inventory host management system.

Features
-----------

* Quick SSH connect. Every seconds matters!
* SSH server inventory. Human brain is optimized for processing not for storage.
* Grouping. Manage your multiple servers with ease by grouping it.
* Ansible inventory like definition file format.

Benefit: 5-15 seconds time saving when switching.

Installation
---------------

    $ python <(curl "https://raw.githubusercontent.com/anvie/tssah/master/tsh.py" -s -N)


Edit `~/.tssah/servers.cfg` and add your own server definition with this format: `name=[SERVER-NAME] host=[HOST] port=[SSH-PORT] user=[LOGIN-NAME]`
Eg:

    name=alpha1 host=123.11.22.33 port=222 user=admin

HOST is optional, if not set Tssah will use SERVER-NAME as host.

PORT is optional, default is 22.

LOGIN-NAME is optional, if not set Tssah will use user name taken from TSSAH_USER environment variable, otherwise Tssah will
get from USER environment variable.

You can also just write like this:

[staging]
staging1.example.com
staging2.example.com

or like this:

[staging]
staging1.example.com host=192.168.1.10

Setting default user name to access to server:

    $ export TSSAH_USER=robin


Usage
------

To see usage, just run:

    $ tsh

Example output:

    USAGE:
            $ tsh [SERVER-NAME]

    Example:
            $ tsh alpha1

    To listing all registered servers and it data, just run it with param `ls`, eg:

            $ tsh ls

    To check all servers is up or down:

            $ tsh ping

    REGISTERED SERVERS:

    alpha1               alpha2

