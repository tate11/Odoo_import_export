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

model = ['stock.inventory.line']

new_file = []
unidades = {'UND': 'Unit(s)', 'GR': 'g', 'KG': 'kg', 'MTS': 'm', 'LTS': 'Liter(s)',
            'GL': 'gal(s)', 'BOL': 'Bol', 'BOT': 'Bot', 'CC': 'cc'}
SustitucionesLocation = {}
SustitucionesInventory = {}
SustitucionesProduct = {}
SustitucionesUnidad = {}

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

        location = record['location_id']
        if location.find('Almacen') > 0:
            location = location.replace("Almacen", "Almacén")
        inventory = record['name']
        product = record['product_id']
        unidad = record['product_uom']
        cantidad = record['product_qty']

        reconectar = True
        while reconectar:
            try:

                if location not in SustitucionesLocation:
                    id_location = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'stock.location', 'search_read',
                                                     [[['name', '=', location]]], {'fields': ['name']})
                    if len(id_location) > 0:
                        SustitucionesLocation[location] = id_location[0]['id']
                    else:
                        SustitucionesLocation[location] = location

                if inventory not in SustitucionesInventory:
                    id_inventory = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'stock.inventory', 'search_read',
                                                      [[['name', '=', inventory]]], {'fields': ['name']})
                    if len(id_inventory) > 0:
                        SustitucionesInventory[inventory] = id_inventory[0]['id']
                    else:
                        SustitucionesInventory[inventory] = inventory

                if product not in SustitucionesProduct:
                    id_product = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'product.product', 'search_read',
                                                    [[['default_code', '=', product]]], {'fields': ['name']})
                    if len(id_product) > 0:
                        SustitucionesProduct[product] = id_product[0]['id']
                    else:
                        SustitucionesProduct[product] = product

                if unidad not in SustitucionesUnidad:
                    id_unidad = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'product.uom', 'search_read',
                                                   [[['name', '=', unidades[unidad]]]], {'fields': ['name']})
                    if len(id_unidad) > 0:
                        SustitucionesUnidad[unidad] = id_unidad[0]['id']
                    else:
                        SustitucionesUnidad[unidad] = unidad

                inventorys = {'location_id/.id': SustitucionesLocation[location],
                             'inventory_id/.id': SustitucionesInventory[inventory], 'product_id/.id': SustitucionesProduct[product], 'product_uom_id/.id': SustitucionesUnidad[unidad], 'product_qty': cantidad}
                print(inventorys)
                new_file.append(inventorys)
                reconectar = False
            except:
                print(sys.exc_info())

print("sobreescribiendo")
new_header = list(new_file[0].keys())
with open("DATA/Datos/" + model[0] + '.csv', 'w', encoding="ISO-8859-1") as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=new_header)
    writer.writeheader()
    for record in new_file:
        writer.writerow(record)
