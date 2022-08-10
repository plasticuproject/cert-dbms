#!/usr/bin/python3
"""manage.py"""

from sys import argv
from sys import exit as sys_exit
from typing import Any, Optional
import subprocess
import datetime
import sqlite3
import pathlib

PATH = pathlib.Path.cwd()

HELP_TEXT = """
Usage: manage.py [-h] database

-h, --help          bring up this help message
database            name of cert database
"""

MENU_TEXT = """
####################
# [1] LIST CERTS   #
# [2] VIEW CURRENT #
# [3] VIEW CERT    #
# [4] UPDATE CERT  #
# [5] EXTRACT CERT #
# [6] QUIT         #
####################
"""

UPDATE_TEXT = """
###########################
# [1] DATE ADDED          #
# [2] USED                #
# [3] DATE APPLIED        #
# [4] BANNED              #
# [5] DATE BANNED         #
# [6] REQUIRES ACTIVATION #
# [7] CURRENTLY IN USE    #
###########################
"""


def list_certs(cursor_obj: sqlite3.Cursor) -> None:
    """List all cert names in DATABASE."""
    cursor_obj.execute('select * from certs')
    rows = cursor_obj.fetchall()
    for row in rows:
        cursor_obj.execute(f'select banned from certs where id = "{row[0]}"')
        is_banned = cursor_obj.fetchall()[0][0]
        if is_banned == 1:
            print(f"BANNED\t{row[0]}")
        else:
            print(f"\t{row[0]}")


def print_cert(name: str, cursor_obj: sqlite3.Cursor) -> None:
    """Print cert data."""
    try:
        cursor_obj.execute(f'select * from certs where id is "{name}"')
        cert_data = cursor_obj.fetchall()
        bools = {0: "No", 1: "Yes"}
        print(f"""
                               Name:  {cert_data[0][0]}
                         Date Added:  {cert_data[0][1]}
                               Used:  {bools[cert_data[0][2]]}
                       Date Applied:  {cert_data[0][3]}
                             Banned:  {bools[cert_data[0][4]]}
                        Date Banned:  {cert_data[0][5]}
                Requires Activation:  {bools[cert_data[0][6]]}
                   Currently In Use:  {bools[cert_data[0][7]]}\n""")
    except IndexError:
        print("\n[!] Invalid Cert Name [!]")


def view_cert(cursor_obj: sqlite3.Cursor) -> None:
    """View cert data."""
    name = input("[*] Cert Name: ")
    print_cert(name, cursor_obj)


def update_cert(con: sqlite3.Connection, cursor_obj: sqlite3.Cursor) -> None:
    """Manually update values for specific cert."""
    cases = ["1", "2", "3", "4", "5", "6", "7"]
    bools = {"no": "0", "yes": "1"}
    bool_items = ["applied", "banned", "required_activation", "currently_used"]
    name = input("[*] Cert name: ")
    print_cert(name, cursor_obj)
    print(UPDATE_TEXT)
    update_choice = input("\n[*] Update Which Value: ")
    if update_choice in cases:
        item = update_switch(update_choice)
        value = input("[*] Updated Value: ")
        if item in bool_items:
            if value.lower() == "no" or value.lower() == "yes":
                value = bools[value.lower()]
                cursor_obj.execute(f'UPDATE certs SET {item} = "{value}" '
                                   f'where id is "{name}"')
                con.commit()
            else:
                print('\n[!] Expected YES or NO Value [!]')
        else:
            none_safe_value: Optional[str] = None if value == "" else value
            cursor_obj.execute(
                f'UPDATE certs SET {item} = "{none_safe_value}" '
                'where id is "{name}"')
            con.commit()
        print_cert(name, cursor_obj)
    else:
        print("\n[!] Invalid Choice [!]")


def extract_cert(cert_dir: str, con: sqlite3.Connection,
                 cursor_obj: sqlite3.Cursor) -> None:
    """Extract new cert and update DATABASE for used and new cert."""
    cursor_obj.execute(
        'select id from certs where banned is "0" and currently_used is "0"')
    rows = cursor_obj.fetchall()
    try:
        name = rows[0][0]
        cert_loc = PATH / cert_dir[:-3] / name
        subprocess.run(["./bpi-extract.sh", cert_loc], check=False)
        print(f"\n[#] EXTRACTED: {name} [#]")
        applied = str(datetime.datetime.now())
        cursor_obj.execute(
            'UPDATE certs SET banned = "1" where currently_used is "1"')
        cursor_obj.execute(f'UPDATE certs SET banned_date = "{applied}" '
                           'where currently_used is "1"')
        cursor_obj.execute(
            'UPDATE certs SET currently_used = "0" where currently_used is "1"'
        )
        cursor_obj.execute(
            f'UPDATE certs SET currently_used = "1" where id is "{name}"')
        cursor_obj.execute(
            f'UPDATE certs SET date_applied = "{applied}" where id is "{name}"'
        )
        cursor_obj.execute(
            f'UPDATE certs SET applied = "1" where id is "{name}"')
        print("[#] UPDATED DATABASE [#]\n")
        print_cert(name, cursor_obj)
        con.commit()
    except IndexError:
        print("[!] No Available Certs [!]")


def menu_switch(case: str, cert_dir: str, con: sqlite3.Connection,
                cursor_obj: sqlite3.Cursor) -> None:
    """Main menu switch."""
    switch = {
        "1": list_certs,
        "2": view_current,
        "3": view_cert,
        "4": update_cert,
        "5": extract_cert,
        "6": leave
    }
    function_call: Any = switch[case]
    if case in ["1", "2", "3"]:
        function_call(cursor_obj)
    elif case == "5":
        function_call(cert_dir, con, cursor_obj)
    elif case == "6":
        function_call()
    else:
        function_call(con, cursor_obj)


def update_switch(case: str) -> str:
    """Update cert switch."""
    switch = {
        "1": "date_added",
        "2": "applied",
        "3": "date_applied",
        "4": "banned",
        "5": "banned_date",
        "6": "required_activation",
        "7": "currently_used"
    }
    return switch[case]


def leave() -> None:
    """Exit program."""
    print()
    sys_exit()


def view_current(cursor_obj: sqlite3.Cursor) -> None:
    """Print cert that is currently in use."""
    cursor_obj.execute('select id from certs where currently_used is "1"')
    rows = cursor_obj.fetchall()
    try:
        name = rows[0][0]
        print()
        print_cert(name, cursor_obj)
    except IndexError:
        print("\n[!] No Cert Currently In Use [!]")


def menu(cert_dir: str, con: sqlite3.Connection,
         cursor_obj: sqlite3.Cursor) -> None:
    """Main menu."""
    cases = ["1", "2", "3", "4", "5", "6"]
    while True:
        print(MENU_TEXT)
        choice = input("[*] Choice: ")
        if choice not in cases:
            continue
        menu_switch(choice, cert_dir, con, cursor_obj)


if __name__ == "__main__":

    # Check for help flag
    if len(argv) < 2 or argv[1] == "--help" or argv[1] == "-h":
        print(HELP_TEXT)
        sys_exit()

    # Check if file name is valid, run stuff if so
    if (PATH / argv[1]).suffix == ".db":
        CON = sqlite3.connect(argv[1])
        CURSOR_OBJ = CON.cursor()
        print(type(CON), type(CURSOR_OBJ))
        try:
            CURSOR_OBJ.execute("select * from certs")
        except sqlite3.DatabaseError:
            print(f"\n[*] {argv[1]} is not the cert database file\n")
            sys_exit()
        try:
            menu(argv[1], CON, CURSOR_OBJ)
        except KeyboardInterrupt:
            sys_exit()
    else:
        print(f"\n[*] {argv[1]} is not a valid database file\n")
