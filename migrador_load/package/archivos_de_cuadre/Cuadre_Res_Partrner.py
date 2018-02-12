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

model = ['res.partner']

new_file = []
inventory_name = {}
SustitucionesLocation = {}

print("Conectando")

var_type_convert = {'CEDULA DE CIUDADANIA': 13,
                    'NIT': 31, 'TARJETA IDENTIDAD': 12}


def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
    SOCK = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(URL_11))
    SOCK_CONMMON = xmlrpclib.ServerProxy(
        '{}/xmlrpc/2/common'.format(URL_11))
    UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
    return SOCK, UID


SOCK_11, UID_11 = connectOdooWebServices(
    URL_11, DB_11, USERNAME_11, PASSWORD_11)

cities = {}
states = {}
countries = {}
partners = {}
var_types = {}

print("leyendo cvs")
with open('../../DATA/External_Data/' + model[0] + '.csv', encoding="ISO-8859-1") as csvfile:
    records = csv.DictReader(csvfile)
    for record in records:
        city = record['city_id']
        state = record['state_id']
        country = record['country_id']
        partner = record['partner_id']
        var_type = record['vat_type']
        print
        if city not in cities:
            id_city = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.country.state.city', 'search_read',
                                         [[['name', '=', city]]], {'fields': ['name']})
            if len(id_city) > 0:
                cities[city] = id_city[0]['id']
            else:
                cities[city] = city
        if state not in states:
            id_state = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.country.state', 'search_read',
                                          [[['name', '=', state]]], {'fields': ['name']})
            if len(id_state) > 0:
                states[state] = id_state[0]['id']
            else:
                states[state] = state

        if country not in countries:
            id_country = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.country', 'search_read',
                                            [[['name', '=', country]]], {'fields': ['name']})
            if len(id_country) > 0:
                countries[country] = id_country[0]['id']
            else:
                countries[country] = country

        if partner not in partners:
            id_partner = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.partner', 'search_read',
                                            [[['name', '=', partner]]], {'fields': ['name']})
            if len(id_partner) > 0:
                partners[partner] = id_partner[0]['id']
            else:
                partners[partner] = partner

        if var_type not in var_types:
            var_types[var_type] = var_type_convert[var_type]

        record['city_id'] = cities[city]
        record['state_id'] = states[state]
        record['country_id'] = countries[country]
        record['partner_id'] = partners[partner]
        record['var_type'] = var_types[var_type]

        new_file.append(record)

print("sobreescribiendo")
new_header = list(new_file[0].keys())
with open("../../DATA/Datos/" + model[0] + '.csv', 'w', encoding="ISO-8859-1") as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=new_header)
    writer.writeheader()
    for record in new_file:
        writer.writerow(record)
