import xmlrpc.client as xmlrpclib
import csv
import time
import sys

URL_11 = "https://klarens.odoo.com"
DB_11 = "klarens-cti-master-12521"
USERNAME_11 = 'admin'
PASSWORD_11 = '0doo.admin'


def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
    SOCK = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(URL_11))
    SOCK_CONMMON = xmlrpclib.ServerProxy(
        '{}/xmlrpc/2/common'.format(URL_11))
    UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
    return SOCK, UID


def saveAttributes(FIELDS_RECORDS, name):
    with open(name, 'w', encoding="ISO-8859-1") as csvfile:
        fieldnames = list(FIELDS_RECORDS[0].keys())
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in FIELDS_RECORDS:
            writer.writerow(record)


SOCK_11, UID_11 = connectOdooWebServices(
    URL_11, DB_11, USERNAME_11, PASSWORD_11)
model = 'res.partner'
errors = []
print('leyendo. . .')
with open("DATA/Eliminate_Data/" + model + '.csv', encoding="ISO-8859-1") as infile:
    read_records = csv.reader(infile)
    count = 0
    for record in read_records:
        if count < 1:
            count += 1
        else:
            FIELDS_RECORDS = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'hr.department', 'search_read', [
                [('name', '=', record)]], {'fields': ['name']})
            for ids in FIELDS_RECORDS:
                try:
                    error = SOCK_11.execute_kw(
                        DB_11, UID_11, PASSWORD_11, 'hr.department', 'unlink', [[ids['id']]])
                except:
                    errors.append(ids)
saveAttributes(errors, 'errors_respartner')
