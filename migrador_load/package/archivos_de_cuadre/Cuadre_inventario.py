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

model = ['stock.inventory']

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

print("leyendo cvs")
with open("DATA/Datos/" + model[0] + '.csv', encoding="ISO-8859-1") as csvfile:
    records = csv.DictReader(csvfile)
    for record in records:
        accounting_date = record['accounting_date']
        date = record['date']
        location = record['location_id']
        if location.find('Almacen') > 0:
            location = location.replace("Almacen", "Almacén")
        name = record['name']

        if name not in inventory_name:
            inventory_name[name] = 0
            if location not in SustitucionesLocation:
                id_location = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'stock.location', 'search_read',
                                                 [[['name', '=', location]]], {'fields': ['name']})
                if len(id_location) > 0:
                    SustitucionesLocation[location] = id_location[0]['id']
                else:
                    SustitucionesLocation[location] = location

            inventory = {'accounting_date': accounting_date,
                         'date': date, 'name': name, 'location_id': SustitucionesLocation[location], 'filter': 'partial'}

            new_file.append(inventory)

print("sobreescribiendo")
new_header = list(new_file[0].keys())
with open("DATA/Datos/" + model[0] + '.csv', 'w', encoding="ISO-8859-1") as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=new_header)
    writer.writeheader()
    for record in new_file:
        writer.writerow(record)
