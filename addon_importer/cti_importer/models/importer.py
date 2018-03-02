# -*- coding: utf-8 -*-

import base64
import csv
import logging
import socket
import xmlrpc.client as xmlrpclib
import time
import os

from datetime import datetime

from openerp import fields, models

_logger = logging.getLogger('IMPORTER')


class ImporterData(models.Model):
    _name = "importer.data"

    name = fields.Char(string='Name', required=False)
    db = fields.Char(string='db', required=True)
    url = fields.Char(string='url', required=True)
    username = fields.Char(string='username', required=True)
    password = fields.Char(string='password', required=True)
    path = fields.Char(string='Path', default='/tmp/')
    model = fields.Char(string='model', required=True)

    def connectOdooWebServices(self):
        sock = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        sock_common = xmlrpclib.ServerProxy(
            '{}/xmlrpc/2/common'.format(self.url))
        uid = sock_common.login(self.db, self.username, self.password)
        return sock, uid

    def migrate(self, file, model, sock, db, uid, password):
        all_errors = []
        sizeDocument = os.path.getsize("DATA/" + file + "/" + model + '.csv')
        errors = ''
        attributes = []
        with open("DATA/Datos/" + model + '.csv', encoding="ISO-8859-1") as csvfile:
            records = csv.reader(csvfile)
            header = 0
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
                    try:
                        record_to_migrate = []
                        record_to_migrate.append(record)
                        position = attributes.index('acc_number')
                        new_data = {}
                        id_record = sock.execute_kw(db, uid, password, model, 'search_read',
                                                    [[('acc_number', '=', record[position])]], {'fields': ['name']})
                        if len(id_record) > 0:
                            my_id = id_record[0]['id']
                            for i in range(0, len(record)):
                                new_data[attributes[i]] = record[i]
                            update = sock.execute_kw(db, uid, password, model, 'write', [
                                [int(my_id)], new_data])
                            print(update)
                        else:
                            data = [attributes, record_to_migrate]
                            errors = sock.execute_kw(
                                db, uid, password, model, 'load', data)
                            if len(errors['messages']) > 0 and errors['messages'][0]['type'] == 'error':
                                all_errors.append(
                                    errors['messages'][0]['message'])
                    except:
                        'hola'
                        # position1 = attributes.index('department_id/.id')
                        # position2 = attributes.index('job_id/.id')
                        # print(record[position1], ",", record[position2])

        return all_errors, attributes

    def my_import(self):
        print("Conectando a " + self.url + " . . .")
        sock, uid = self.connectOdooWebServices()
        # models = models(sock, db_import, uid, password_import)
        model = self.model

        #i = 0
        # while i < len(model):
        print('Importando', model, '. . .')
        errors, attributes = self.migrate(
            'Datos', model, sock, self.db, uid, self.password)
        #i += 1

    def main(self):
        self.connectOdooWebServices()


class ImporterDataModels(models.Model):
    _name = 'importer.data.models'

    models_id = fields.Many2one('ir.model', string='Model', required=True)
    importer_id = fields.Many2one(
        'importer.data', string='Importer', required=True, ondelete='cascade')
    exporter = fields.Boolean(string='Exporter?', default=True)
    read_time = fields.Char(string='Read time')
    write_time = fields.Char(string='Write time')
    count = fields.Char(string='Count')
    fields_len = fields.Char(string='Fields len')
    limit = fields.Integer(string='Limit')
    condition = fields.Char(string='Condition', default="['active','=',True]")
    file = fields.Binary(string='File')
    file_name = fields.Char(string='File name')
