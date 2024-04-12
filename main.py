import requests
import json
import csv
import pandas

import keycloak_methods

# TODO: Pandas Excel
# TODO: Funktionen auslagern
# TODO: Setup vollständig (Gruppen, Attribute)
# TODO: Website

import logging

logger = logging.getLogger('keycloak-access')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# logger.addHandler(fh)
logger.addHandler(ch)


keycloak_methods.keycloak_server ='http://localhost:8080'

keycloak_user = 'admin'
keycloak_password = 'admin'

realm_name = 'myrealm'
attribute_name = 'testattribut'
clients = ['client1', 'client2']
remove_roles = ['uma_authorization', 'offline_access']
role_names = ['role_default', 'role_all', 'role_some']
user_names = ['user_default', 'user_all', 'user_some']

# GET /{realm}/groups/{id}/role-mappings/clients/{client}/composite


access_token = keycloak_methods.get_access_token(keycloak_user, keycloak_password)
headers = {'Authorization': 'Bearer ' + access_token}

# create_realm(headers, realm_name)
#
# for role_name in role_names:
#     create_realm_role(headers, realm_name, role_name)
#
# for user_name in user_names:
#     create_realm_user(headers, realm_name, user_name)
#     userid = get_user_by_name(headers, realm_name, user_name)['id']
#     for role_name in role_names:
#         role = get_role_by_name(headers, realm_name, role_name)
#         add_role_to_user(headers, realm_name, userid, role)

result_users = []

for user in keycloak_methods.get_users(headers, realm_name):
    result_roles = keycloak_methods.get_effective_roles_by_user(headers, realm_name, user['id'])
    result_role_names = [r['name'] for r in result_roles]
    result_role_names.remove(f"default-roles-{realm_name}")
    for remove_role in remove_roles:
        result_role_names.remove(remove_role)

    client_role_names = []
    for client in clients:
        client_roles = keycloak_methods.get_effective_client_roles_by_user(headers, realm_name, client, user['id'])
        client_role_names.extend([r['name'] for r in client_roles])

    result_groups = keycloak_methods.get_groups_by_user(headers, realm_name, user['id'])
    result_group_names = [r['name'] for r in result_groups]
    result_group_attributes = [r.get('attributes', {}) for r in result_groups]

    result_attributes = []
    for attribute in result_group_attributes:
        result_attributes.extend(attribute.get(attribute_name, []))
    result_attributes.extend(user.get('attributes', {}).get(attribute_name, {}))

    result_users.append({'Nutzername': user['username'],
                         'Leserollen': ','.join(result_role_names),
                         'Funktionsrollen': ','.join(client_role_names),
                         'Gruppen': ','.join(result_group_names),
                         'Attribute': ','.join(result_attributes)})


print(result_users)

with open('Berechtigungen.csv', 'w', newline='') as fo:
    dict_writer = csv.DictWriter(fo, fieldnames=result_users[0].keys(), delimiter=';')
    dict_writer.writeheader()
    dict_writer.writerows(result_users)

import pandas as pd
pd.DataFrame(result_users).to_excel('Berechtigungen.xlsx')


