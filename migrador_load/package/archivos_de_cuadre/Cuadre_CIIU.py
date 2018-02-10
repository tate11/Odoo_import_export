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

model = ['account.ciiu.lines']

new_file = []
SustitucionesCIIU = {}
SustitucionesCITY = {}
SustitucionesTAX = {}

print("Conectando")


def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
    SOCK = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(URL_11))
    SOCK_CONMMON = xmlrpclib.ServerProxy(
        '{}/xmlrpc/2/common'.format(URL_11))
    UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
    return SOCK, UID


SOCK_11, UID_11 = connectOdooWebServices(
    URL_11, DB_11, USERNAME_11, PASSWORD_11)
print("leyendo cvs")
with open("DATA/Datos/" + model[0] + '.csv') as csvfile:
    records = csv.DictReader(csvfile)
    for record in records:
        print(record)
        ciiu = record['ciiu_id/.id']
        city = record['city_id/.id']
        tax = record['tax_id/.id']
        if ciiu not in SustitucionesCIIU:
            id_ciiu = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'account.ciiu', 'search_read',
                                         [[['name', '=', ciiu]]], {'fields': ['name']})
            if len(id_ciiu) > 0:
                SustitucionesCIIU[ciiu] = id_ciiu[0]['id']
            else:
                SustitucionesCIIU[ciiu] = ciiu

        if city not in SustitucionesCITY:
            id_city = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.country.state.city', 'search_read',
                                         [[['name', '=', city]]], {'fields': ['name', 'code']})

            if len(id_city) > 0:
                SustitucionesCITY[city] = id_city[0]['id']
            else:
                SustitucionesCITY[city] = city

        if tax not in SustitucionesTAX:
            id_tax = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'account.tax', 'search_read',
                                        [[['name', '=', 'RteIca ' + tax + '‰>c']]], {'fields': ['name']})

            if len(id_tax) > 0:
                SustitucionesTAX[tax] = id_tax[0]['id']
            else:
                SustitucionesTAX[tax] = tax

        record['ciiu_id/.id'] = SustitucionesCIIU[ciiu]
        record['city_id/.id'] = SustitucionesCITY[city]
        record['tax_id/.id'] = SustitucionesTAX[tax]

        new_file.append(record)
print("sobreescribiendo")
new_header = list(new_file[0].keys())
with open("DATA/Datos/" + model[0] + '.csv', 'w') as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=new_header)
    writer.writeheader()
    for record in new_file:
        writer.writerow(record)
