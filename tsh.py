#!/usr/bin/env python
# Tssah just SSH easy connector utility
#

import sys
import os
import re
import subprocess

from os.path import expanduser

HOME = os.path.join(expanduser("~"), ".tssah")
USER = os.environ.get("TSSAH_USER", "")
if len(USER.strip()) == 0:
    USER = os.environ["USER"]

def ensure_home():
    if not os.path.isdir(HOME):
        os.makedirs(HOME)

def show_banner():
    print("")
    print("TSSAH - v2.2.0")
    print("A painless ssh switcher")
    print("")

def show_usage(servers):
    cmd_name = sys.argv[0]
    s = cmd_name.split("/")
    if len(s) > 1:
        cmd_name = s[-1]
    show_banner()
    print("USAGE:")
    print("        $ %s [SERVER-NAME]" % cmd_name)
    print("")
    print("Example:")
    print("        $ %s alpha1" % cmd_name)
    print("")
    print("To listing all registered servers and it params, just run it with param `ls`, eg:\n")
    print("        $ %s ls" % cmd_name)
    print("")
    print("Listing only for specific group, eg: webserver group:")
    print("")
    print("        $ %s ls webserver" % cmd_name)
    print("")
    print("To check all servers is up or down:")
    print("")
    print("        $ %s ping" % cmd_name)
    print("")
    print("REGISTERED SERVERS:\n")
    _server_names = map(lambda a: a["name"], servers)
    print_sorted_list(_server_names, columns=3, ljust=20)
    print("\n")


def print_sorted_list(data, rows=0, columns=0, ljust=10):
    """
    Prints sorted item of the list data structure formated using
    the rows and columns parameters
    This function taken from: https://stackoverflow.com/a/33464001
    """

    if not data:
        return

    if rows:
        # column-wise sorting
        # we must know the number of rows to print on each column
        # before we print the next column. But since we cannot
        # move the cursor backwards (unless using ncurses library)
        # we have to know what each row with look like upfront
        # so we are basically printing the rows line by line instead
        # of printing column by column
        lines = {}
        for count, item in enumerate(sorted(data)):
            lines.setdefault(count % rows, []).append(item)
        for key, value in sorted(lines.items()):
            for item in value:
                print(item.ljust(ljust)),
            print()
    elif columns:
        # row-wise sorting
        # we just need to know how many columns should a row have
        # before we print the next row on the next line.
        for count, item in enumerate(sorted(data), 1):
            print(item.ljust(ljust)),
            if count % columns == 0:
                print()
    else:
        print(sorted(data))  # the default print behaviour

import platform
import subprocess

def ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    FNULL = open(os.devnull, 'w')
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT) == 0

def ping_servers(servers):
    up = 0
    down = 0
    for server in servers:
        resp = ping(server["host"])
        if resp:
            print(" + %s (%s) is UP" % (server["name"], server["host"]))
            up = up + 1
        else:
            print(" - %s (%s) is DOWN" % (server["name"], server["host"]))
            down = down + 1

    print("-----")
    print("UP: %d, DOWN: %d" % (up, down))


def read_server_file(server_file):
    global USER

    server_list = []

    if server_file.endswith(".txt"):
        def to_js(a):
            if len(a) == 4:
                return {"name": a[0], "host": a[1], "port": a[2], "user_name": a[3], "group": "etc"}
            else:
                return {"name": a[0], "host": a[1], "port": a[2], "user_name": "", "group": "etc"}

        with open(server_file, "r") as f:
            _servers = f.readlines()
            _servers = filter(lambda a: not a.startswith("#"), _servers)
            _servers = map(lambda a: a.strip(), _servers)
            _servers = filter(lambda x: len(x) > 5, _servers)
            _servers_s = map(lambda a: re.split("\\s+", a), _servers)
            server_list = map(to_js, _servers_s)

    else:
        groups = []
        group = "etc"
        with open(server_file, "r") as f:
            _loaded_names = []
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    group = line[1:-1]
                    groups.append(group)
                else:
                    ss = re.split(" +", line)
                    svr = {"group": group}
                    if len(ss) > 1:
                        for s in ss:
                            if s.startswith("name="):
                                svr["name"] = s.split("=")[1]
                                if svr["name"] in _loaded_names:
                                    raise Exception("server `%s` already defined before, please check your tssah server definition file" % svr["name"])
                                _loaded_names.append(svr["name"])
                            elif s.startswith("host="):
                                svr["host"] = s.split("=")[1]
                            elif s.startswith("port="):
                                svr["port"] = s.split("=")[1]
                            elif s.startswith("user="):
                                svr["user_name"] = s.split("=")[1]
                            elif s.startswith("key="):
                                svr["key"] = s.split("=")[1]
                        if svr and "name" not in svr:
                            svr["name"] = ss[0].strip()
                        if svr and "host" not in svr:
                            # raise Exception("ERROR: server `%s` has no host" % svr["name"])
                            svr["host"] = svr["name"] # use name as it host
                        if svr:
                            if "port" not in svr:
                                svr["port"] = "22"
                            if "user_name" not in svr:
                                svr["user_name"] = USER
                            server_list.append(svr)
                        

                    elif len(ss) == 1 and len(ss[0]) > 1:
                        svr["name"] = ss[0]
                        svr["host"] = ss[0]
                        svr["port"] = "22"
                        svr["user_name"] = USER
                        server_list.append(svr)

    return list(server_list)


def load_servers():

    server_txt = os.path.join(HOME, "servers.txt")
    server_ini = os.path.join(HOME, "servers.cfg")

    servers = []    

    if os.path.exists(server_txt):
        servers = read_server_file(server_txt)
    # else:
    #     with open(server_txt, "w") as f:
    #         f.write("# Add your servers here\n")
    #         f.write("# Using this format: [NAME] [IP-OR-HOST-NAME] [PORT] [USER]\n")
    #         f.write("# Eg:\n")
    #         f.write("# alpha1 123.11.22.33 771 root\n")

    if os.path.exists(server_ini):
        servers.extend(read_server_file(server_ini))
    else:
        with open(server_ini, "w") as f:
            f.write("# Add your server definition here\n")
            f.write("# Eg:\n")
            f.write("#[office]\n")
            f.write("#web.alpha1.net\n")
            f.write("#name=alpha1 host=123.11.22.33 port=222 user=admin\n")
            f.write("#name=alpha1 host=123.11.22.33\n")

    return servers

def ensure_installed():

    # check for existance
    # install automatically if the binary file not found
    BIN = "/usr/local/bin/tsh"
    if not os.path.exists(BIN):

        yn = raw_input("It's look like you are not installed this cool tool, do you want to install? [Y/n] ").strip()
        if yn.lower() in ["y", "yes", "ok", "yeah"]:

            print("Installing...")

            sudo_cmd = ""
            if not os.access(os.path.dirname(BIN), os.W_OK | os. X_OK):
                print("Need write permission to install tssah. Sudo command is needed...")
                sudo_cmd = "sudo "

            os.system(sudo_cmd + "wget https://raw.githubusercontent.com/anvie/tssah/master/tsh.py -O " + BIN)
            os.system(sudo_cmd + "chmod +x " + BIN)
            print("Done.")


def main():
    ensure_home()

    ensure_installed()
    servers = load_servers()

    if len(sys.argv) < 2:
        show_usage(servers)
        return 2

    if sys.argv[1] == "--version":
        show_banner()
        return 0

    elif sys.argv[1] == "ping":
        ping_servers(servers)
        return 0

    elif sys.argv[1] == "ls":
        
        grouped_servers = {}
        for x in servers:
            grouped_servers.setdefault(x['group'], []).append(x)

        tgroup = None
        if len(sys.argv) > 2:
            tgroup = sys.argv[2].strip()


        print("\nSERVERS:")

        def print_servers_group(group, groups):
            print("\n----- %s -----" % group)
            for sv in groups[group]:                
                user_name = USER
                if len(sv["user_name"]) > 0:
                    user_name = sv["user_name"]

                print("  - %s host=%s port=%s user=%s" % (sv["name"], sv["host"], sv["port"], user_name))

        if tgroup:
            if tgroup not in grouped_servers:
                return
            else:
                print_servers_group(tgroup, grouped_servers)
        else:
            for group, items in grouped_servers.items():
                if group == "etc": # ditunda
                    continue
                print_servers_group(group, grouped_servers)
                

            for group, sv in grouped_servers.items():
                if group == "etc":
                    print_servers_group(group, grouped_servers)

        print("")
        return


    name = sys.argv[1]

    try:

        sv = (a for a in servers if a["name"].lower() == name.lower()).next()
        print("Connecting %s..." % sv["name"])

        _user = USER
        if len(sv["user_name"].strip()) > 0:
            _user = sv["user_name"]

        target = "%s@%s" % (_user, sv["host"])
        print("target: " + target)

        add_opts = []
        
        if sv.has_key("key"):
            add_opts.append("-i " + sv["key"])
            
        os.system("ssh %s %s -p %s" % (target, " ".join(add_opts).strip(), sv["port"]))

    except StopIteration:
        print("No server with name %s" % name)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
