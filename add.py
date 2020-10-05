#!/usr/bin/python3

from sys import argv
import datetime
import sqlite3
import pathlib

path = pathlib.Path.cwd()

helpText = '''
Usage: add.py [-h] directory

-h, --help          bring up this help message
directory           directory with certs to add
'''


def addCerts(cert_dir):

    # If DATABASE does not exist, initialize it
    if (path / 'cert.db').is_file() == False: # pylint: disable=E1101
        con = sqlite3.connect('cert.db')
        cursor_obj = con.cursor()
        cursor_obj.execute('CREATE TABLE certs(id text PRIMARY KEY, date_added text, applied integer, date_applied text, banned integer, banned_date text, required_activation integer, currently_used integer)')

    # Add new cert file info for all UNIQUE cert files from directory
    con = sqlite3.connect('cert.db')
    cursor_obj = con.cursor()
    added_certs = []
    skipped_certs = []
    add_path = path / cert_dir
    for cert_file in add_path.iterdir():

        # Check that file in directory is indeed a cert file and set values
        if cert_file.is_file() and cert_file.suffix == '.txt': #TODO find file sig
            cert_name = cert_file.name
            added = datetime.datetime.now()
            entities = (cert_name, added, 0, 0, 0, 0)

            # Try to add UNIQUE cert file to DATABASE
            try:
                cursor_obj.execute('INSERT INTO certs(id, date_added, applied, banned, required_activation, currently_used) VALUES(?, ?, ?, ?, ?, ?)', entities)
                con.commit()
                added_certs.append(cert_name)

            # If cert file is already in DATABASE then skip
            except sqlite3.IntegrityError:
                skipped_certs.append(cert_name)
    con.close()

    # Print output
    if len(skipped_certs) > 0:
        print('\n[*] Already in DATABASE, skipping:\n')
        [print('\t' + x) for x in skipped_certs]
    if len(added_certs) > 0:
        print('\n\n[*] Added to the DATABASE:\n')
        [print('\t' + x) for x in added_certs]
    print(f'\n\n[*] Added: {len(added_certs)}')
    print(f'[*] Skipped {len(skipped_certs)}\n')


if __name__ == '__main__':

    # Check for help flag
    if len(argv) < 2 or argv[1] == '--help' or argv[1] == '-h':
        print(helpText)
        quit()

    # Check if directory name is valid, run stuff if so
    if (path / argv[1]).is_dir():
        try:
            addCerts(argv[1])
        except KeyboardInterrupt:
            quit()
    else:
        print(f'\n[*] {argv[1]} not a valid directory\n')

