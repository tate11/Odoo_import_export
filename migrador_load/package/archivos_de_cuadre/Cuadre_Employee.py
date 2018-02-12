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

model = ['hr.employee']

new_file = []
inventory_name = {}
SustitucionesLocation = {}

print("Conectando")

gender_dic = {'F': 'female', 'M': 'male'}
marital_dic = {'SOLTERO': 'single', 'CASADO': 'married',
               'DIVORCIADO': 'divorced', 'UNION LIBRE': 'married', 'VIUDO': 'widower'}


def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
    SOCK = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(URL_11))
    SOCK_CONMMON = xmlrpclib.ServerProxy(
        '{}/xmlrpc/2/common'.format(URL_11))
    UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
    return SOCK, UID


SOCK_11, UID_11 = connectOdooWebServices(
    URL_11, DB_11, USERNAME_11, PASSWORD_11)

departments = {}
jobs = {}
countries = {}
addresses = {}
genders = {}
martials = {}

print("leyendo cvs")
with open('../../DATA/External_Data/' + model[0] + '.csv', encoding="ISO-8859-1") as csvfile:
    records = csv.DictReader(csvfile)
    for record in records:
        department = record['department_id']
        job = record['job_id']
        country = record['country_id']
        address = record['address_home_id']
        gender = record['gender']
        marital = record['marital']
        birthay = record['birthay']
        birthay = birthay[0:4] + '-' + birthay[4:6] + \
            '-' + birthay[6:len(birthay)]

        if department not in departments:
            id_department = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'hr.department', 'search_read',
                                               [[['name', '=', department]]], {'fields': ['name']})
            if len(id_department) > 0:
                departments[department] = id_department[0]['id']
            else:
                departments[department] = department
        if job not in jobs:
            id_job = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'hr.job', 'search_read',
                                        [[['name', '=', job]]], {'fields': ['name']})
            if len(id_job) > 0:
                jobs[job] = id_job[0]['id']
            else:
                jobs[job] = job

        if country not in countries:
            id_country = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.country', 'search_read',
                                            [[['name', '=', country]]], {'fields': ['name']})
            if len(id_country) > 0:
                countries[country] = id_country[0]['id']
            else:
                countries[country] = country

        if address not in addresses:
            id_address = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'res.partner', 'search_read',
                                            [[['name', '=', address]]], {'fields': ['name']})
            if len(id_address) > 0:
                addresses[address] = id_address[0]['id']
            else:
                addresses[address] = address

        if gender in gender_dic:
            genders[gender] = gender_dic[gender]

        if marital in marital_dic:
            martials[marital] = marital_dic[marital]

        record['department_id'] = departments[department]
        record['job_id'] = jobs[job]
        record['country_id'] = countries[country]
        record['address_id'] = addresses[address]
        record['gender'] = genders[gender]
        record['martial'] = martials[marital]
        record['birthay'] = birthay

        new_file.append(record)

print("sobreescribiendo")
new_header = list(new_file[0].keys())
with open("../../DATA/Datos/" + model[0] + '.csv', 'w', encoding="ISO-8859-1") as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=new_header)
    writer.writeheader()
    for record in new_file:
        writer.writerow(record)
