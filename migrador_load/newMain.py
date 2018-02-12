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


def connectOdooWebServices(url, db, username, password):
    sock = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    sock_common = xmlrpclib.ServerProxy(
        '{}/xmlrpc/2/common'.format(url))
    uid = sock_common.login(db, username, password)
    return sock, uid


def models(sock, db, uid, password):
    id_models = sock.execute_kw(db, uid, password, 'ir.model',
                                'search', [[['transient', '=', False]]], {})
    all_models = sock.execute_kw(db, uid, password, 'ir.model', 'read',
                                 [id_models], {'fields': ['model']})
    i = 0
    while i < len(all_models):
        name = all_models[i]["model"]
        if 'abstract' in name or 'ir.' in name or 'base' in name or 'im' in name or 'bus' in name or 'board' in name or 'event' in name or 'form' in name or 'iap' in name or 'link' in name or 'note' in name or 'report' in name or 'resource' in name or 'website' in name or 'wizard' in name:
            all_models.pop(i)
        else:
            i += 1
    return all_models


def changeNoBooleanData(record, attributes):
    for data in record.keys():
        if data != 'id':
            if record[data] == False and attributes[data]['ttype'] != 'boolean':
                record[data] = ''
    return record


def change_to_idDB(file, model, attributes):
    new_file = []
    with open("DATA/" + file + "/" + model + '.csv', encoding="ISO-8859-1") as infile:
        read_records = csv.reader(infile)
        new_header = []
        for attribute in attributes.keys():
            new_header.append(attributes[attribute]['name'])
        count = 0
        for record in read_records:
            if count < 1:
                new_file.append(new_header)
                count += 1
            else:
                new_file.append(record)

    with open("DATA/" + file + "/" + model + '.csv', 'w', encoding="ISO-8859-1") as outfile:
        write_records = csv.writer(outfile)
        for record in new_file:
            write_records.writerow(record)


def createCvs(file, sock, db, uid, password, model, attributes, id_records):
    read_records = sock.execute_kw(db, uid, password, model, 'read',
                                   [id_records], {'fields': list(attributes.keys())})
    print('\t Creando cvs de ' + file + ' . . .')
    with open("DATA/" + file + "/" + model + '.csv', 'w', encoding="ISO-8859-1") as csvfile:
        fieldnames = list(attributes.keys())
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in read_records:
            record = changeNoBooleanData(record, attributes)
            writer.writerow(record)
    change_to_idDB(file, model, attributes)


def createBigCvs(file, sock, db, uid, password, model, attributes, id_records):
    print("big Data")


def adjustCVS(file, sock, db, uid, password, model, attributes):
    id_records = sock.execute_kw(
        db, uid, password, model, 'search', [[]])

    if len(id_records) > 3000:
        createBigCvs(file, sock, db, uid, password,
                     model, attributes, id_records)
    else:
        createCvs(file, sock, db, uid, password, model, attributes, id_records)


def organizeAtributes(attributes):
    new_attributes_dic = {}
    for attribute in attributes:
        name = attribute['name']
        new_name = attribute['name']
        relation = attribute['relation']
        ttype = attribute['ttype']
        if '_id' in new_name and relation:
            new_name = new_name + '/.id'
        new_attributes_dic[name] = {
            'name': new_name.strip('\n'), 'relation': relation, 'ttype': ttype}
    new_attributes_dic['id'] = {
        'name': 'id', 'relation': False, 'ttype': ''}
    return new_attributes_dic


def my_export(url_origin, db_origin, username_origin, password_origin, url_destine, db_destine, username_destine, password_destine):
    print("\t exportando...")

    print("Conectando a " + url_destine + " . . .")
    sock_destine, uid_destine = connectOdooWebServices(
        url_destine, db_destine, username_destine, password_destine)

    print("Conectando a " + url_origin + " . . .")
    sock_origin, uid_origin = connectOdooWebServices(
        url_origin, db_origin, username_origin, password_origin)

    # models = models(sock_destine, db_destine, uid_destine, password_destine)
    models = [{'model': 'hr.employee'}]

    i = 0
    while i < len(models):
        model = models[i]['model']
        characteritics_of_attributes = sock_destine.execute_kw(db_destine, uid_destine, password_destine, 'ir.model.fields', 'search_read', [
            ['&', ('model', '=', model), '&', ('readonly', '=', False), '|', ('required', '=', True), ('relation', '=', False)]], {'fields': ['name', 'relation', 'ttype']})
        attributes = organizeAtributes(characteritics_of_attributes)
        adjustCVS("Datos", sock_origin, db_origin, uid_origin,
                  password_origin, model, attributes)
        i += 1


def actualizate():
    ids = []
    vats = []
    with open('errors_respartner', encoding="ISO-8859-1") as csvfile:
        records = csv.reader(csvfile)
        for record in records:
            ids.append(record[0])
            vats.append(record[2])
    return ids, vats


def migrate(file, model, sock, db, uid, password):
    # Temporal
    ids, vats = actualizate()
    #####
    all_errors = []
    sizeDocument = os.path.getsize("DATA/" + file + "/" + model + '.csv')
    with open("DATA/" + file + "/" + model + '.csv', encoding="ISO-8859-1") as csvfile:
        records = csv.reader(csvfile)
        header = 0
        attributes = []
        record_to_migrate = []
        limit = 500
        for record in records:
            if header < 1:
                attributes = record[:]
                header += 1
            elif 'ref' in attributes:
                if record[attributes.index('ref')] != '':
                    record_to_migrate.append(record)
                else:
                    data = [attributes, record_to_migrate]

                    errors = sock.execute_kw(
                        db, uid, password, model, 'load', data)

                    record_to_migrate = []
                    record_to_migrate.append(record)
            elif sizeDocument > 99999999999999999999999999999999:
                if limit == 0:
                    data = [attributes, record_to_migrate]
                    errors = sock.execute_kw(
                        db, uid, password, model, 'load', data)
                    record_to_migrate = []
                    record_to_migrate.append(record)
                else:
                    record_to_migrate.append(record)
            else:
                record_to_migrate = []
                record_to_migrate.append(record)
                position = attributes.index()
                if record[position] in vats:
                    attributes.append('id/.id')
                    record_to_migrate.append(ids[vats.index(record[position])])
                data = [attributes, record_to_migrate]
                errors = sock.execute_kw(
                    db, uid, password, model, 'load', data)

                if len(errors['messages']) > 0 and errors['messages'][0]['type'] == 'error':
                    all_errors.append(errors['messages'][0]['message'])

    return all_errors


def my_import(url, db, username, password):
    print('\t Importando')
    print("Conectando a " + url + " . . .")
    sock, uid = connectOdooWebServices(
        url, db, username, password)
    # models = models(sock, db_import, uid, password_import)
    models = [{'model': 'hr.employee'}]
    i = 0
    while i < len(models):
        model = models[i]['model']
        errors = migrate('Datos', model, sock, db, uid, password)
        print(errors)
        i += 1


def main():
    # url_import = "https://klarens.odoo.com"
    # db_import = "klarens-cti-master-12521"
    # username_import = 'admin'
    # password_import = '0doo.admin'

    url_import = "https://klarens-staging-20231.dev.odoo.com"
    db_import = "klarens-staging-20231"
    username_import = 'admin'
    password_import = '0doo.admin'

    url_export = "http://vallenata.test.3rp.la"
    db_export = "vallenata"
    username_export = 'admin'
    password_export = '0doo.admin'

    print("1. Exportar")
    print("2. Importar")
    print("3. Exportar/Importar")

    export_import = sys.stdin.readline().strip("\n")

    export_odoo = False
    import_odoo = False

    if export_import == '1':
        export_odoo = True
    elif export_import == '2':
        import_odoo = True
    elif export_import == '3':
        export_odoo = True
        import_odoo = True

    if export_odoo:
        my_export(url_export, db_export, username_export, password_export,
                  url_import, db_import, username_import, password_import)
    if import_odoo:
        my_import(url_import, db_import, username_import, password_import)


main()
