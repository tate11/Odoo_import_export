# -*- coding: utf-8 -*-

import base64
import csv
import logging
import socket
import xmlrpc.client
from datetime import datetime

from openerp import fields, models

_logger = logging.getLogger('IMPORTER')


class ImporterData(models.Model):
    _name = "importer.data"

    name = fields.Char(string='Name', required=True)
    dbname = fields.Char(string='dbname', required=True)
    host = fields.Char(string='host', required=True)
    user = fields.Char(string='user', required=True)
    password = fields.Char(string='password', required=True)
    path = fields.Char(string='Path', default='/tmp/')
    models_ids = fields.One2many('importer.data.models', 'importer_id', string='Models', required=True)
    type = fields.Selection([('imp', 'Importer'), ('exp', 'Exporter')], string='Type', required=True)

    def get_models(self):
        models = self.env['ir.model'].search([])
        for x in models:
            self.write({'models_ids': (0, 0, {'model_id': x.id, 'exporter': True})})

    def connection(self):
        _logger.info('connection')
        common = xmlrpc.client.ServerProxy('{host}/xmlrpc/2/common'.format(host=self.host))
        socket.setdefaulttimeout(7200)
        uid = common.authenticate(self.dbname, self.user, self.password, {})
        _logger.info(common.version())
        _logger.info(uid)
        models = xmlrpc.client.ServerProxy('{host}/xmlrpc/2/object'.format(host=self.host), allow_none=True)

        for model in self.models_ids:
            if model.exporter:
                start = datetime.now()
                condition, condition_a, fields_list = [], [], []
                fields = models.execute_kw(self.dbname, uid, self.password, model.models_id.model, 'fields_get', [],
                                           {'attributes': ['string', 'name', 'type', 'readonly']})
                model.fields_len = str(len(fields))
                _logger.info('fields len: ' + model.fields_len)
                for field in fields.keys():
                    if not fields.get(field).get('readonly'):
                        fields_list.append(field)
                condition_a.append(eval(model.condition))
                condition.append(condition_a)
                count = models.execute_kw(self.dbname, uid, self.password,
                                          model.models_id.model, 'search_count',
                                          condition)
                model.count = count
                _logger.info('register count: ' + str(model.count))
                datas = models.execute_kw(self.dbname, uid, self.password, model.models_id.model, 'search_read',
                                          condition,
                                          {'fields': fields_list, 'limit': model.limit})
                model.read_time = str(datetime.now() - start)
                _logger.info('read model: ' + model.models_id.model + ' time: ' + str(model.read_time))
                start = datetime.now()
                # titles
                data_keys = False
                for data in datas:
                    if not data_keys:
                        data_keys = data.keys()
                        break
                titles = list(data_keys)
                myData = []
                myData.append(titles)
                lines = ''
                for data in datas:
                    lines = []
                    for t in titles:
                        dat = data.get(t) or ''
                        if type(dat) == list:
                            dat = dat[0]   or ''
                        lines.append(dat)
                    myData.append(lines)

                path = '/tmp/' + model.models_id.model + '.csv'
                myFile = open(path, 'w')
                with myFile:
                    writer = csv.writer(myFile)
                    writer.writerows(myData)
                model.write_time = str(datetime.now() - start)
                model.write(
                    {'file_name': model.models_id.model + '.csv', 'file': base64.b64encode(open(path, 'rb').read())})
                _logger.info('write model: ' + model.models_id.model + ' time: ' + str(model.write_time))
        return True


class ImporterDataModels(models.Model):
    _name = 'importer.data.models'

    models_id = fields.Many2one('ir.model', string='Model', required=True)
    importer_id = fields.Many2one('importer.data', string='Importer', required=True, ondelete='cascade')
    exporter = fields.Boolean(string='Exporter?', default=True)
    read_time = fields.Char(string='Read time')
    write_time = fields.Char(string='Write time')
    count = fields.Char(string='Count')
    fields_len = fields.Char(string='Fields len')
    limit = fields.Integer(string='Limit')
    condition = fields.Char(string='Condition', default="['active','=',True]")
    file = fields.Binary(string='File')
    file_name = fields.Char(string='File name')
