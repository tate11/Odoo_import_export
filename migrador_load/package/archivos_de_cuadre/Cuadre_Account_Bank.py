#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# This Python file uses the following encoding: utf-8
#
#
# sys.setdefaultencoding('utf-8')


import xmlrpc.client as xmlrpclib
import csv
from time import time
import sys


URL_11 = "https://klarens.odoo.com"
DB_11 = "klarens-cti-master-12521"
USERNAME_11 = 'admin'
PASSWORD_11 = '0doo.admin'

model = ['res.partner.bank']

new_file = []
inventory_name = {}
SustitucionesLocation = {}

print("Conectando")


def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
    SOCK = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(URL_11))
    SOCK_CONMMON = xmlrpclib.ServerProxy(
        '{}/xmlrpc/2/common'.format(URL_11))
    UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
    return SOCK, UID


SOCK_11, UID_11 = connectOdooWebServices(
    URL_11, DB_11, USERNAME_11, PASSWORD_11)

partners = {}
banks = {'0': ''}

print("leyendo cvs")
with open('../../DATA/External_Data/' + model[0] + '.csv', encoding="ISO-8859-1") as csvfile:
    records = csv.DictReader(csvfile)
    for record in records:
        try:
            partner = record['partner_id']
            bank = record['bank_id']
            print(bank)
            print(partner)

            if partner not in partners:
                id_partner = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.partner', 'search_read',
                                                [[['vat', '=', partner]]], {'fields': ['name']})
                if len(id_partner) > 0:
                    partners[partner] = id_partner[0]['id']
                else:
                    partners[partner] = partner
            if bank not in banks:
                id_bank = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.bank', 'search_read',
                                             [[['bic', '=', bank]]], {'fields': ['name']})
                if len(id_bank) > 0:
                    banks[bank] = id_bank[0]['id']
                else:
                    banks[bank] = bank

            record['partner_id'] = partners[partner]
            record['bank_id'] = banks[bank]

            new_file.append(record)
        except:
            print(sys.exc_info())

print("sobreescribiendo")
new_header = list(new_file[0].keys())
with open("../../DATA/Datos/" + model[0] + '.csv', 'w', encoding="ISO-8859-1") as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=new_header)
    writer.writeheader()
    for record in new_file:
        writer.writerow(record)
