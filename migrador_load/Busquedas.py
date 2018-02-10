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
    with open(name, 'w') as csvfile:
        fieldnames = list(FIELDS_RECORDS[0].keys())
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in FIELDS_RECORDS:
            writer.writerow(record)


print("conectando datos...")
SOCK_11, UID_11 = connectOdooWebServices(
    URL_11, DB_11, USERNAME_11, PASSWORD_11)

model = "stock.inventory.line"

FIELDS_RECORDS = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'ir.model.fields', 'search_read', [
                                    ['&', ('model', '=', model),'&',('readonly','=',False), '|', ('required', '=', True), ('relation', '=', False)]], {'fields': ['model', 'name', 'relation', 'readonly', 'required']})

# FIELDS_RECORDS = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.partner', 'search_read',
#                                     [[['vat', '=', '892301290']]], {'fields': ['name']})

saveAttributes(FIELDS_RECORDS, "prueba.atributtes.csv")
print(FIELDS_RECORDS)
exit()
