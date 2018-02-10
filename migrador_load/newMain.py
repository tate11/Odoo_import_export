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


def my_export(sock, url, db, username, password, models):
    print("Conectando a " + url + " . . .")
    sock, uid = connectOdooWebServices(
        url, db, username, password)

    i = 0
    while i < len(models):
        model = models[i]['model']
        fields_records = sock.execute_kw(db, uid, password, 'ir.model.fields', 'search_read', [
            ['&', ('model', '=', model), '&', ('readonly', '=', False), '|', ('required', '=', True), ('relation', '=', False)]], {'fields': ['name', 'relation']})

    print("exportando...")


def migrate(file, model, sock, db, uid, password):
    errors = ''
    sizeDocument = os.path.getsize("DATA/" + file + "/" + model + '.csv')
    with open("DATA/" + file + "/" + model + '.csv', encoding="ISO-8859-1") as csvfile:
        records = csv.reader(csvfile)
        header = 0
        atributes = []
        record_to_migrate = []
        limit = 500
        for record in records:
            if header < 1:
                attributes = record[:]
                header += 1
            elif 'ref' in atributes:
                if record[atributes.index('ref')] != '':
                    record_to_migrate.append(record)
                else:
                    data = [attributes, record_to_migrate]

                    errors = sock.execute_kw(
                        db, uid, password, model, 'load', data)

                    record_to_migrate = []
                    record_to_migrate.append(record)
            elif sizeDocument > 1610000:
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
                data = [attributes, record_to_migrate]
                errors = sock.execute_kw(
                    db, uid, password, model, 'load', data)

    return errors


def my_import(sock, uid, db, username, password, models):
    print("importando...")


def main():
    url_import = "https://klarens.odoo.com"
    db_import = "klarens-cti-master-12521"
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

    print(export_import)

    if export_import == '1':
        export_odoo = True
    elif export_import == '2':
        import_odoo = True
    elif export_import == '3':
        export_odoo = True
        import_odoo = True

    print("Conectando a " + url_import + " . . .")
    sock, uid = connectOdooWebServices(
        url_import, db_import, username_import, password_import)
    my_models = models(sock, db_import, uid, password_import)

    if export_odoo:
        my_export(sock, url_export, db_export, username_export,
                  password_export, my_models)
    if import_odoo:
        my_import(sock, uid, db_import, username_import,
                  password_import, my_models)


main()
