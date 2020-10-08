#!/usr/bin/python3

from sys import argv
import subprocess
import datetime
import sqlite3
import pathlib

path = pathlib.Path.cwd()

helpText = '''
Usage: manage.py [-h] database

-h, --help          bring up this help message
database            name of cert database
'''

menuText = '''
####################
# [1] LIST CERTS   #
# [2] VIEW CURRENT #
# [3] VIEW CERT    #
# [4] UPDATE CERT  #
# [5] EXTRACT CERT #
# [6] QUIT         #
####################
'''

updateText = '''
###########################
# [1] DATE ADDED          #
# [2] USED                #
# [3] DATE APPLIED        #
# [4] BANNED              #
# [5] DATE BANNED         #
# [6] REQUIRES ACTIVATION #
# [7] CURRENTLY IN USE    #
###########################
'''


def listCerts(cert_dir):

    # List all cert names in DATABASE
    cursor_obj.execute('select * from certs')
    rows = cursor_obj.fetchall()
    for row in rows:
        cursor_obj.execute('select banned from certs where id = "'+row[0]+'"')
        is_banned = cursor_obj.fetchall()[0][0]
        if is_banned == 1:
            print('BANNED\t' + row[0])
        else:
            print('\t' + row[0])


def printCert(name):

    # Print cert data
    try:
        cursor_obj.execute('select * from certs where id is "'+name+'"')
        certData = cursor_obj.fetchall()
        bools = {0: 'No', 1: 'Yes' }
        print(f'''
                               Name:  {certData[0][0]}
                         Date Added:  {certData[0][1]}
                               Used:  {bools[certData[0][2]]}
                       Date Applied:  {certData[0][3]}
                             Banned:  {bools[certData[0][4]]}
                        Date Banned:  {certData[0][5]}
                Requires Activation:  {bools[certData[0][6]]}
                   Currently In Use:  {bools[certData[0][7]]}\n''')
    except IndexError:
        print('\n[!] Invalid Cert Name [!]')


def viewCert(cert_dir):

    # View cert data
    name = input('[*] Cert Name: ')
    printCert(name)


def updateCert(cert_dir):

    # Manually update values for specific cert
    cases = ['1', '2', '3', '4', '5', '6', '7']
    bools = {'no': '0', 'yes': '1'}
    bool_items = ['applied', 'banned', 'required_activation', 'currently_used']
    name = input('[*] Cert name: ')
    printCert(name)
    print(updateText)
    update_choice = input('\n[*] Update Which Value: ')
    if update_choice in cases:
        item = update_switch(update_choice)
        value = input('[*] Updated Value: ')
        if item in bool_items:
            if value.lower() == 'no' or value.lower() == 'yes':
                value = bools[value]
                cursor_obj.execute('UPDATE certs SET ' +item+ '= "'+value+'" where id is "'+name+'"')
                con.commit()
            else:
                print('\n[!] Expected YES or NO Value [!]')
        else:
            if value == '':
                value = 'None'
            cursor_obj.execute('UPDATE certs SET ' +item+ '= "'+value+'" where id is "'+name+'"')
            con.commit()
        printCert(name)
    else:
        print('\n[!] Invalid Choice [!]')


def extractCert(cert_dir):

    # Extract new cert and update DATABASE values for previously used and new cert
    cursor_obj.execute('select id from certs where banned is "0" and currently_used is "0"')
    rows = cursor_obj.fetchall()
    try:
        name = rows[0][0]
        cert_loc = path / cert_dir[:-3] / name
        try:
            subprocess.call(['wine', 'REDACTED.exe', cert_loc], timeout=5)
        except subprocess.TimeoutExpired:
            pass
        print(f'\n[#] EXTRACTED: {name} [#]')
        applied = str(datetime.datetime.now())
        cursor_obj.execute('UPDATE certs SET banned = "1" where currently_used is "1"')
        cursor_obj.execute('UPDATE certs SET banned_date = "'+applied+'" where currently_used is "1"')
        cursor_obj.execute('UPDATE certs SET currently_used = "0" where currently_used is "1"')
        cursor_obj.execute('UPDATE certs SET currently_used = "1" where id is "'+name+'"')
        cursor_obj.execute('UPDATE certs SET date_applied = "'+applied+'" where id is "'+name+'"')
        cursor_obj.execute('UPDATE certs SET applied = "1" where id is "'+name+'"')
        print('[#] UPDATED DATABASE [#]\n')
        printCert(name)
        con.commit()
    except IndexError:
        print('[!] No Available Certs [!]')


def menu_switch(case, cert_dir):

    # Main menu switch
    switch = {'1': listCerts,
              '2': viewCurrent,
              '3': viewCert,
              '4': updateCert,
              '5': extractCert,
              '6': leave
             }
    return switch[case](cert_dir)


def update_switch(case):

    # Update cert switch
    switch = {'1': 'date_added',
              '2': 'applied',
              '3': 'date_applied',
              '4': 'banned',
              '5': 'banned_date',
              '6': 'required_activation',
              '7': 'currently_used'
             }
    return switch[case]


def leave(cert_dir):
    
    # Exit program
    print()
    quit()


def viewCurrent(cer_dir):

    # Print cert that is currently in use
    cursor_obj.execute('select id from certs where currently_used is "1"')
    rows = cursor_obj.fetchall()
    try:
        name = rows[0][0]
        print()
        printCert(name)
    except IndexError:
        print('\n[!] No Cert Currently In Use [!]')


def menu(cert_dir):

    # Main menu
    cases = ['1', '2', '3', '4', '5', '6']
    while True:
        print(menuText)
        choice = input('[*] Choice: ')
        if choice not in cases:
            continue
        else:
            menu_switch(choice, cert_dir)


if __name__ == '__main__':

    # Check for help flag
    if len(argv) < 2 or argv[1] == '--help' or argv[1] == '-h':
        print(helpText)
        quit()

    # Check if file name is valid, run stuff if so
    if (path / argv[1]).suffix == '.db':
        con = sqlite3.connect(argv[1])
        cursor_obj = con.cursor()
        try:
            cursor_obj.execute('select * from certs')
        except sqlite3.DatabaseError:
            print(f'\n[*] {argv[1]} is not the cert database file\n')
            quit()
        try:
            menu(argv[1])
        except KeyboardInterrupt:
            quit()
    else:
        print(f'\n[*] {argv[1]} is not a valid database file\n')

