#!/usr/bin/python3
"""add.py"""

from sys import argv
import datetime
import sqlite3
import pathlib

PATH = pathlib.Path.cwd()

HELP_TEXT = '''
Usage: add.py [-h] directory

-h, --help          bring up this help message
directory           directory with certs to add
'''


def add_certs(cert_dir: str) -> None:
    """Add new certs to database. Initialize database if none exists."""

    # If DATABASE does not exist, initialize it
    d_b = cert_dir + '.db'
    if (PATH / d_b).is_file() is False:
        con = sqlite3.connect(d_b)
        cursor_obj = con.cursor()
        cursor_obj.execute(
            'CREATE TABLE certs(id text PRIMARY KEY, date_added text, applied integer, date_applied text, banned integer, banned_date text, required_activation integer, currently_used integer)'
        )

    # Add new cert file info for all UNIQUE cert files from directory
    con = sqlite3.connect(d_b)
    cursor_obj = con.cursor()
    added_certs = []
    skipped_certs = []
    add_path = PATH / cert_dir
    for cert_file in add_path.iterdir():

        # Check that file in directory is indeed a cert file and set values
        if cert_file.is_file(
        ) and cert_file.suffix == '.txt':  # TODO find file sig
            cert_name = cert_file.name
            added = datetime.datetime.now()
            entities = (cert_name, added, 0, 0, 0, 0)

            # Try to add UNIQUE cert file to DATABASE
            try:
                cursor_obj.execute(
                    'INSERT INTO certs(id, date_added, applied, banned, required_activation, currently_used) VALUES(?, ?, ?, ?, ?, ?)',
                    entities)
                con.commit()
                added_certs.append(cert_name)

            # If cert file is already in DATABASE then skip
            except sqlite3.IntegrityError:
                skipped_certs.append(cert_name)
    con.close()

    # Print output
    if skipped_certs:
        print('\n[*] Already in DATABASE, skipping:\n')
        for _x in skipped_certs:
            print('\t' + _x)
    if added_certs:
        print('\n\n[*] Added to the DATABASE:\n')
        for _x in added_certs:
            print('\t' + _x)
    print(f'\n\n[*] Added: {len(added_certs)}')
    print(f'[*] Skipped {len(skipped_certs)}\n')


if __name__ == '__main__':

    # Check for help flag
    if len(argv) < 2 or argv[1] == '--help' or argv[1] == '-h':
        print(HELP_TEXT)
        quit()

    # Check if directory name is valid, run stuff if so
    if (PATH / argv[1]).is_dir():
        CERT_DIR = argv[1]
        if CERT_DIR[-1] == '/':
            CERT_DIR = CERT_DIR[:-1]
        try:
            add_certs(CERT_DIR)
        except KeyboardInterrupt:
            quit()
    else:
        print(f'\n[*] {argv[1]} not a valid directory\n')
