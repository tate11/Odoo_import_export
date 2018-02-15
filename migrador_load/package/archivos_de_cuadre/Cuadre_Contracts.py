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

model = ['hr.contract']

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
employees = {}

print("leyendo cvs")
with open('../../DATA/External_Data/' + model[0] + '.csv', encoding="ISO-8859-1") as csvfile:
    records = csv.DictReader(csvfile)
    for record in records:
        try:
            department = record['department_id']
            job = record['job_id']
            employee = record['employee_id']
            initial_date = record['date_start']
            final_date = record['date_end']

            if initial_date != 0:
                initial_date = initial_date[0:4] + '-' + initial_date[4:6] + \
                    '-' + initial_date[6:len(initial_date)]
            else:
                initial_date = ''

            if final_date != 0:
                final_date = final_date[0:4] + '-' + final_date[4:6] + \
                    '-' + final_date[6:len(final_date)]
            elif final_date == 'INDEFIN.':
                final_date = ''
            else:
                final_date = ''

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

            if employee not in employees:
                id_employee = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'hr.employee', 'search_read',
                                                [[['name', '=', employee]]], {'fields': ['name']})
                if len(id_employee) > 0:
                    employees[employee] = id_employee[0]['id']
                else:
                    employees[employee] = employee


            record['department_id'] = departments[department]
            record['job_id'] = jobs[job]
            record['employee_id'] = employees[employee]
            record['date_start'] = initial_date
            record['date_end'] = final_date

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
