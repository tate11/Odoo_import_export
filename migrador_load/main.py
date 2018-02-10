#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# This Python file uses the following encoding: utf-8
#
#
# sys.setdefaultencoding('utf-8')

import xmlrpc.client as xmlrpclib
import socket
import csv
import time
import sys
import os


class TimeoutTransport(xmlrpclib.Transport):
    
    def __init__(self, timeout, use_datetime=0):
        self.timeout = timeout
        # xmlrpclib uses old-style classes so we cannot use super()
        xmlrpclib.Transport.__init__(self, use_datetime)

    def make_connection(self, host):
        connection = xmlrpclib.Transport.make_connection(self, host)
        connection.timeout = self.timeout
        return connection


class TimeoutServerProxy(xmlrpclib.ServerProxy):

    def __init__(self, uri, timeout=14500, transport=None, encoding=None, verbose=0, allow_none=0, use_datetime=0):
        t = TimeoutTransport(timeout)
        xmlrpclib.ServerProxy.__init__(
            self, uri, t, encoding, verbose, allow_none, use_datetime)


def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
    SOCK = TimeoutServerProxy('{}/xmlrpc/2/object'.format(URL_11))
    SOCK_CONMMON = TimeoutServerProxy('{}/xmlrpc/2/common'.format(URL_11))
    UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
    return SOCK, UID

# def connectOdooWebServices(URL_11, DB_11, USERNAME_11, PASSWORD_11):
#     SOCK = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(URL_11))
#     SOCK_CONMMON = xmlrpclib.ServerProxy(
#         '{}/xmlrpc/2/common'.format(URL_11))
#     UID = SOCK_CONMMON.login(DB_11, USERNAME_11, PASSWORD_11)
#     return SOCK, UID


def errorsOfReading(model_error, error):
    data = {}
    print("Creando CSV  de ERRORES de lectura. . .")
    atributtes = ["MODELO", "ERROR"]
    with open('ERRORES_de_lectura .csv', 'a') as csvfile_error:
        fieldnames_error = atributtes
        writer_error = csv.DictWriter(
            csvfile_error, fieldnames=fieldnames_error)
        writer_error.writeheader()
        data["MODELO"] = model_error
        data['ERROR'] = error
        writer_error.writerow(data)


def models(SOCK_11, DB_11, UID_11, PASSWORD_11):
    MODELS_11 = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'ir.model',
                                   'search', [[['transient', '=', False]]], {})
    RECORD_11 = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'ir.model', 'read',
                                   [MODELS_11], {'fields': ['model']})

    print("\t Descartando modelos . . .")
    i = 0
    while i < len(RECORD_11):
        NAME = RECORD_11[i]["model"]
        if 'abstract' in NAME or 'ir.' in NAME or 'base' in NAME or 'im' in NAME or 'bus' in NAME or 'board' in NAME or 'event' in NAME or 'form' in NAME or 'iap' in NAME or 'link' in NAME or 'note' in NAME or 'report' in NAME or 'resource' in NAME or 'website' in NAME or 'wizard' in NAME:
            MODELS_11.remove(RECORD_11[i]["id"])
            RECORD_11.pop(i)
        else:
            i += 1
    return RECORD_11


def headerOfDocument(file, errors, model_error, attributes):
    attributes.insert(0, 'External_ID')
    attributes.append('other_error')
    with open("ERRORES/" + file + "/" + model_error + '.csv', 'w') as csvfile:
        fieldnames = attributes
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writeheader()


def saveError(file, errors, model_error, attributes, externalID):
    data = {}
    data["External_ID"] = externalID

    for error in errors['messages']:
        try:
            data[error['field']] = error['message']
        except:
            data['other_error'] = error['message']
    with open("ERRORES/" + file + "/" + model_error + '.csv', 'a') as csvfile:
        fieldnames = attributes
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writerow(data)
    return 1


def changeListData(attributes_original, record, MY_FIELD_RECORDS_11):
    i = 0
    while i < len(record):
        if ('_id' in attributes_original[i] or '_uid' in attributes_original[i])and type(attributes_original[i]) != bool:
            model = MY_FIELD_RECORDS_11[attributes_original[i]]['relation']
            model = model.replace('.', '_')
            data = record[i]
            data = data.replace(']', '')
            data = data.replace('[', '')
            data = data.replace(' ', '')
            data = data.replace(
                ',', ',' + model + '_')
            if data != '':
                data = model + '_' + data
            record[i] = data
        i += 1
    return record


def changeIDSHeaders(attributes_migrate):
    i = 0
    while i < len(attributes_migrate):
        if ('_ids' in attributes_migrate[i] or '_uid' in attributes_migrate[i])and not '/id' in attributes_migrate[i]:
            attributes_migrate[i] = attributes_migrate[i] + "/id"
        i += 1
    return attributes_migrate


def migrate(file, model, SOCK_11, DB_11, UID_11, PASSWORD_11, MY_FIELD_RECORDS_11):
    numberOfErrors = 0
    completeRecord = []
    sizeDocument = os.path.getsize("DATA/" + file + "/" + model + '.csv')
    errors = ''
    with open("DATA/" + file + "/" + model + '.csv', encoding="ISO-8859-1") as csvfile:
        records = csv.reader(csvfile)
        title = 0
        attributes_migrate = []
        attributes_original = []
        validate = False
        count = 0
        time_1 = time.time()
        print(">>>", time.strftime("%I:%M:%S"), "<<<")
        for record in records:
            print(record)
            if title == 0:
                attributes_migrate = record[:]
                # attributes_migrate = changeIDSHeaders(attributes_migrate)
                attributes_original = record[:]
                title += 1
            else:
                # record = changeListData(
                #     attributes_original, record, MY_FIELD_RECORDS_11)
                # campos = [attributes_migrate, [record]]
                if sizeDocument > 0:
                    if record[1] != '':
                        count += 1

                    if count > 1:
                        campos = [attributes_migrate, completeRecord]
                        reconect = True
                        while reconect:
                            try:
                                errors = SOCK_11.execute_kw(
                                    DB_11, UID_11, PASSWORD_11, model, 'load', campos)
                                reconect = False
                            except:
                                reconect = False
                                print('error!!')

                        if len(errors['messages']) > 0:
                            with open('descuadres.csv', 'a') as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow(
                                    [completeRecord[0][2], completeRecord[0][0], errors['messages'][0]['message']])
                        count = 1
                        completeRecord = []
                        completeRecord.append(record)
                    else:
                        completeRecord.append(record)
                else:
                    completeRecord.append(record)

    campos = [attributes_migrate, completeRecord]
    errors = SOCK_11.execute_kw(
        DB_11, UID_11, PASSWORD_11, model, 'load', campos)
    time_2 = time.time()
    final_time = time_2 - time_1
    print("tiempo final", final_time)
    print(errors)
    return numberOfErrors


def saveAttributes(FIELDS_RECORDS, name):
    with open(name, 'w') as csvfile:
        fieldnames = list(FIELDS_RECORDS[0].keys())
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in FIELDS_RECORDS:
            writer.writerow(record)


def changeExternalID(record, model):
    export_model = model.replace('.', '_')
    for data in record.keys():
        if data == 'id':
            record[data] = export_model + "_" + str(record[data])
    return record


def changeNoBooleanData(record, MY_FIELD_RECORDS_11):
    for data in record.keys():
        if data != 'id':
            if record[data] == False and MY_FIELD_RECORDS_11[data]['ttype'] != 'boolean':
                record[data] = ''
    return record


def changeNoListData(record):
    for data in record.keys():
        if ('_id' in data or '_uid' in data) and type(record[data]) == list:
            if not '_ids' in data:
                record[data] = record[data][0]
    return record


def createCvs(file, SOCK_10, DB_10, UID_10, PASSWORD_10, model, IDS_RECORDS_10, ATTRIBUTES, MY_FIELD_RECORDS_11):
    READ_RECORDS_10 = SOCK_10.execute_kw(DB_10, UID_10, PASSWORD_10, model, 'read',
                                         [IDS_RECORDS_10], {'fields': ATTRIBUTES})

    with open("DATA/" + file + "/" + model + '.csv', 'w') as csvfile:
        fieldnames = ATTRIBUTES
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in READ_RECORDS_10:
            record = changeNoBooleanData(record, MY_FIELD_RECORDS_11)
            record = changeNoListData(record)
            record = changeExternalID(record, model)
            writer.writerow(record)


def createBigCvs(file, SOCK_10, DB_10, UID_10, PASSWORD_10, model, IDS_RECORDS_10, ATTRIBUTES, MY_FIELD_RECORDS_11):
    print("\t Esto si que es grande!")

    with open("DATA/" + file + "/" + model + '.csv', 'w') as csvfile:
        fieldnames = ATTRIBUTES
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writeheader()

    start = 0
    end = 0
    while end != len(IDS_RECORDS_10):
        end = end + 500
        if end > len(IDS_RECORDS_10):
            end = len(IDS_RECORDS_10)
        print(start, end)
        IDS_RECORDS_10_part = IDS_RECORDS_10[start:end]
        READ_RECORDS_10 = SOCK_10.execute_kw(DB_10, UID_10, PASSWORD_10, model, 'read',
                                             [IDS_RECORDS_10_part], {'fields': ATTRIBUTES})
        if len(READ_RECORDS_10) > 0:
            with open("DATA/" + file + "/" + model + '.csv', 'a') as csvfile:
                fieldnames = ATTRIBUTES
                writer = csv.DictWriter(
                    csvfile, fieldnames=fieldnames)
                for record in READ_RECORDS_10:
                    record = changeNoBooleanData(record, MY_FIELD_RECORDS_11)
                    record = changeNoListData(record)
                    record = changeExternalID(record, model)
                    writer.writerow(record)
        start = end


def adjustCVS(file, SOCK_10, DB_10, UID_10, PASSWORD_10, model, ATTRIBUTES, MY_FIELD_RECORDS_11):
    print('\t Creando cvs de' + file + ' . . .')
    IDS_RECORDS_10 = SOCK_10.execute_kw(
        DB_10, UID_10, PASSWORD_10, model, 'search', [[]])

    if len(IDS_RECORDS_10) > 3000:
        createBigCvs(file, SOCK_10, DB_10, UID_10, PASSWORD_10, model,
                     IDS_RECORDS_10, ATTRIBUTES, MY_FIELD_RECORDS_11)
    else:
        createCvs(file, SOCK_10, DB_10, UID_10, PASSWORD_10, model,
                  IDS_RECORDS_10, ATTRIBUTES, MY_FIELD_RECORDS_11)


def printNotifications(numberOfErrors, i, model, initial_time_1, initial_time_2):
    if numberOfErrors == 0:
        if i == 0:
            print("\t", model, " Migro Datos Exitosamente!")
            final_time_1 = time.time()
            time_1 = final_time_1 - initial_time_1
        else:
            print("\t", model, " Migro Relaciones Exitosamente!")
            final_time_2 = time.time()
            time_2 = final_time_2 - initial_time_2
    else:
        if i == 0:
            print(
                "\t", model, "Tuvo Errores al hacer la migracion de datos revise el documento adjunto . . .")
            final_time_1 = time.time()
            time_1 = final_time_1 - initial_time_1
        else:
            print("\t", model, "Tuvo Errores al hacer la migracion de las relaciones revise el documento adjunto . . .")
            final_time_2 = time.time()
            time_2 = final_time_2 - initial_time_2

    return time_1, time_2


def main():
    URL_11 = "https://klarens.odoo.com"
    DB_11 = "klarens-cti-master-12521"
    USERNAME_11 = 'admin'
    PASSWORD_11 = '0doo.admin'

    URL_10 = "http://vallenata.test.3rp.la"
    DB_10 = "vallenata"
    USERNAME_10 = '3rp'
    PASSWORD_10 = '0doo.3rp'

    print("Conectando Version 11 . . .")
    SOCK_11, UID_11 = connectOdooWebServices(
        URL_11, DB_11, USERNAME_11, PASSWORD_11)

    models_11 = models(SOCK_11, DB_11, UID_11, PASSWORD_11)
    print("Conectando Version 10 . . .")
    SOCK_10, UID_10 = connectOdooWebServices(
        URL_10, DB_10, USERNAME_10, PASSWORD_10)

    # models_11 = [{'model': 'account.fiscal.position.tax'}]
    # models_11 = [{'model': 'res.partner'}]
    # models_11 = [{'model': 'hr.job'}, {'model': 'hr.employee'}, {'model': 'hr.department'}]
    # models_11 = [{'model': 'hr.department'}]
    # , {'model': 'account.move.line'}]
    models_11 = [{'model': 'account.move'}]

    # i = 0
    # while i < len(models_11):
    #     try:
    #         model = models_11[i]['model']
    #         print("----------------", model, "-----------------")
    #         # Creacio de Datos
    #         FIELDS_RECORDS = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'ir.model.fields', 'search_read',
    #                                             [[['readonly', '=', False], ['model', '=', model], ['relation', '=', False]]], {'fields': ['field_description', 'name', 'relation', 'readonly', 'ttype']})

    #         MY_FIELD_RECORDS_11 = {}
    #         for fields in FIELDS_RECORDS:
    #             MY_FIELD_RECORDS_11[fields['name']] = fields
    #         ATTRIBUTES = list(MY_FIELD_RECORDS_11.keys())
    #         ATTRIBUTES.insert(0, 'id')

    #         adjustCVS("Datos", SOCK_10, DB_10, UID_10, PASSWORD_10,
    #                   model, ATTRIBUTES, MY_FIELD_RECORDS_11)

    #         # Creacio de Relaciones
    #         FIELDS_RECORDS = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'ir.model.fields', 'search_read',
    #                                             [[['readonly', '=', False], ['model', '=', model], ['relation', '!=', False]]], {'fields': ['field_description', 'name', 'relation', 'readonly', 'ttype']})
    #         MY_FIELD_RECORDS_11 = {}
    #         for fields in FIELDS_RECORDS:
    #             MY_FIELD_RECORDS_11[fields['name']] = fields
    #         ATTRIBUTES = list(MY_FIELD_RECORDS_11.keys())
    #         ATTRIBUTES.insert(0, 'id')
    #         adjustCVS("Relaciones", SOCK_10, DB_10, UID_10,
    #                   PASSWORD_10, model, ATTRIBUTES, MY_FIELD_RECORDS_11)
    #     except:
    #         errorsOfReading(model, sys.exc_info())
    #     i += 1

    time_1 = time.time()
    time_2 = time.time()
    j = 0
    while j < 2:
        while len(models_11) > 0:
            my_model = models_11.pop(0)
            # try:
            model = my_model['model']
            print("----------------", model, "-----------------")
            print("\t Migrando datos . . .")
            FIELDS_RECORDS = SOCK_11.execute_kw(DB_11, UID_11, PASSWORD_11, 'ir.model.fields', 'search_read',
                                                [[['readonly', '=', False], ['model', '=', model]]], {'fields': ['field_description', 'name', 'relation', 'ttype']})
            MY_FIELD_RECORDS_11 = {}
            for fields in FIELDS_RECORDS:
                MY_FIELD_RECORDS_11[fields['name']] = fields
            if j == 0:

                initial_time_1 = time.time()
                numberOfErrors = migrate(
                    "Datos", model, SOCK_11, DB_11, UID_11, PASSWORD_11, MY_FIELD_RECORDS_11)
                # time_1, time_2 = printNotifications(
                #    numberOfErrors, j, model, time_1, time_2)
                #print("La migracion duro:", time_1 + time_2, "seg")
            else:
                print("\t Migrando relaciones . . .")

                initial_time_2 = time.time()
                numberOfErrors = migrate(
                    "Relaciones", model, SOCK_11, DB_11, UID_11, PASSWORD_11, MY_FIELD_RECORDS_11)

                # time_1, time_2 = printNotifications(
                #    numberOfErrors, j, model, time_1, time_2)
                #print("La migracion duro:", time_1 + time_2, "seg")

        j += 1


main()
