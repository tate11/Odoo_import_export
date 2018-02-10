import xmlrpc.client as xmlrpclib
import csv
from time import time
import sys

URL_11 = "https://klarens.odoo.com"
DB_11 = "klarens-cti-master-12521"
USERNAME_11 = 'admin'
PASSWORD_11 = '0doo.admin'

model = ['account.move']


def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
    SOCK = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(URL_11))
    SOCK_CONMMON = xmlrpclib.ServerProxy(
        '{}/xmlrpc/2/common'.format(URL_11))
    UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
    return SOCK, UID


SOCK_11, UID_11 = connectOdooWebServices(
    URL_11, DB_11, USERNAME_11, PASSWORD_11)

new_file = []
Errores = []
SustitucionesTIN = {}
SustitucionesACCOUNT = {}

with open('kls_substitute.csv') as csvfile:
    records_substitute = csv.DictReader(csvfile)
    for record_substitute in records_substitute:
        if record_substitute['field'] == 'account_id':
            SustitucionesACCOUNT[record_substitute['src']
                                 ] = record_substitute['dest']


with open("DATA/Datos/" + model[0] + '.csv') as csvfile:
    records = csv.DictReader(csvfile)
    for record in records:
        TIN = record['line_ids/partner_id']
        if TIN in SustitucionesTIN:
            record['line_ids/partner_id'] = SustitucionesTIN[TIN]
        else:
            FIELDS_RECORDS = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.partner', 'search_read',
                                                [[['vat', '=', TIN]]], {'fields': ['name', 'vat']})
            if len(FIELDS_RECORDS) == 0:
                record['line_ids/partner_id'] = '99999999'
                Errores.append('No Hay un Contacto asociado')
                SustitucionesTIN[record['line_ids/partner_id']] = '99999999'
            elif len(FIELDS_RECORDS) > 1:
                record['line_ids/partner_id'] = '99999999'
                SustitucionesTIN[record['line_ids/partner_id']] = '99999999'
                Errores.append('Hay mas de un contacto asociado')
            else:
                SustitucionesTIN[record['line_ids/partner_id']
                                 ] = record['line_ids/partner_id']
                Errores.append('')

####################################################################################################################

        ACCOUNT = record['line_ids/account_id']
        if ACCOUNT in SustitucionesACCOUNT:
            record['line_ids/account_id'] = SustitucionesACCOUNT[ACCOUNT]
        else:
            FIELDS_RECORDS = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'account.account', 'search_read',
                                                [[['code', '=', ACCOUNT]]], {'fields': ['code']})
            if len(FIELDS_RECORDS) == 0:
                record['line_ids/account_id'] = '939529'
                SustitucionesACCOUNT[record['line_ids/account_id']] = '939529'
                Errores.append('No Hay un Contacto asociado')
            elif len(FIELDS_RECORDS) > 1:
                record['line_ids/partner_id'] = '939529'
                SustitucionesACCOUNT[record['line_ids/account_id']] = '939529'
                Errores.append('Hay mas de un contacto asociado')
            else:
                SustitucionesTIN[record['line_ids/account_id']
                                 ] = record['line_ids/partner_id']
                Errores.append('')
        new_file.append(record)
        print(record)

new_header = list(new_file[0].keys())
with open("DATA/Datos/" + model[0] + '.csv', 'w') as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=new_header)
    writer.writeheader()
    for record in new_file:
        writer.writerow(record)

# print('generando archivo de errores')
# with open("ERRORES/Datos" + model[0] + '.csv', 'w') as csvfile:
#     writer = csv.writer(csvfile)
#     for record in Errores:
#         writer.writerow(record)
