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


def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
    SOCK = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(URL_11))
    SOCK_CONMMON = xmlrpclib.ServerProxy(
        '{}/xmlrpc/2/common'.format(URL_11))
    UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
    return SOCK, UID


SOCK_11, UID_11 = connectOdooWebServices(
    URL_11, DB_11, USERNAME_11, PASSWORD_11)

cities = {}
SustitucionesCIIU = {'0': ''}
property_payment_terms = {'0': ''}
property_supplier_payment_terms = {'0': ''}

print("leyendo cvs")
with open('../../DATA/External_Data/' + model[0] + '.csv', encoding="ISO-8859-1") as csvfile:
    records = csv.DictReader(csvfile)
    for record in records:
        city = record['city_id']
        ciiu = record['ciiu_id']
        property_payment_term = record['property_payment_term_id']
        property_supplier_payment_term = record['property_supplier_payment_term_id']

        if city not in cities:
            id_city = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.country.state.city', 'search_read',
                                         [[['name', '=', city]]], {'fields': ['name']})
            if len(id_city) > 0:
                cities[city] = id_city[0]['id']
            else:
                cities[city] = city

        if ciiu not in SustitucionesCIIU:
            id_ciiu = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'account.ciiu', 'search_read',
                                         [[['name', '=', ciiu]]], {'fields': ['name']})
            if len(id_ciiu) > 0:
                SustitucionesCIIU[ciiu] = id_ciiu[0]['id']
            else:
                SustitucionesCIIU[ciiu] = ciiu

        if property_payment_term not in property_payment_terms:
            id_property_payment_term = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'account.payment.term', 'search_read',
                                                          [[['name', '=', property_payment_term]]], {'fields': ['name']})
            if len(id_property_payment_term) > 0:
                property_payment_terms[property_payment_term] = id_property_payment_term[0]['id']
            else:
                property_payment_terms[property_payment_term] = property_payment_term

        if property_supplier_payment_term not in property_supplier_payment_terms:
            id_property_supplier_payment_term = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'account.payment.term', 'search_read',
                                                                   [[['name', '=', property_supplier_payment_term]]], {'fields': ['name']})
            if len(id_property_payment_term) > 0:
                property_supplier_payment_terms[property_supplier_payment_term] = id_property_supplier_payment_term[0]['id']
            else:
                property_supplier_payment_terms[property_supplier_payment_term] = property_supplier_payment_term
        record['city_id'] = cities[city]
        record['ciiu_id'] = SustitucionesCIIU[ciiu]
        record['property_payment_term_id'] = property_payment_terms[property_payment_term]
        record['property_supplier_payment_term_id'] = property_supplier_payment_terms[property_supplier_payment_term]
        new_file.append(record)

print("sobreescribiendo")
new_header = list(new_file[0].keys())
with open("../../DATA/Datos/" + model[0] + '.csv', 'w', encoding="ISO-8859-1") as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=new_header)
    writer.writeheader()
    for record in new_file:
        writer.writerow(record)
