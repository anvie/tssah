TO SSH AH (TSSAH)
====================

don't ask me the motivation behind the naming.

This is tiny utility to help terminal users organize and help connecting their servers through SSH.

Installation
---------------

    $ curl https://raw.githubusercontent.com/anvie/tssah/master/tssah -sSf | python


Edit `~/.tssah/servers.txt` and add your own servers with this format: `[NAME] [IP-OR-HOST-NAME] [PORT] [USER-NAME]`
Eg:

    alpha1 123.11.22.33 22

USER-NAME is optional, if not set Tssah will use user name taken from TSSAH_USER environment variable, otherwise Tssah will
get from USER environment variable.

Setting default user name to access to server:

    $ export TSSAH_USER=robin


Usage
------

To see usage, just run:

    $ tssah

Example output:

    USAGE:
            $ tssah [SERVER-NAME]

    Example:
            $ tssah alpha1

    To listing all registered servers and it data, just run it with param `--ls`, eg:

            $ tssah --ls

    To add new server, just run it with param `--add [SERVER-NAME]`, eg:

            $tssah --add alpha1

    REGISTERED SERVERS:

    alpha1               alpha2
