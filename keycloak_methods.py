import requests
import logging

logger = logging.getLogger('keycloak-access')

keycloak_server = None

def get_access_token(username, password):
    path = '/auth/realms/master/protocol/openid-connect/token'
    data = {'grant_type': 'password', 'username': username, 'password': password, 'client_id': 'admin-cli'}
    response = requests.post(url=keycloak_server + path, data=data)
    if not response.raise_for_status():
        return response.json()['access_token']


def create_realm(headers, realm_name):
    data = {'enabled': True, 'realm': realm_name, 'id': realm_name}
    response = requests.post(url=keycloak_server + '/auth/admin/realms', headers=headers, json=data)
    if response.status_code == 409:
        logger.debug(f"Realm {realm_name} already exists")
        return response.text
    if not response.raise_for_status():
        logger.debug(f"Created realm {realm_name}")
        return response.text


def get_realms(headers):
    response = requests.get(url=keycloak_server + '/auth/admin/realms', headers=headers)
    if not response.raise_for_status():
        logger.debug(response.text)
        return response.json()


def create_realm_role(headers, realm_name, name, description=''):
    # POST
    # 	http://localhost:8080/auth/admin/realms/myrealm/roles
    data = {'description': description, 'name': name}
    response = requests.post(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/roles", headers=headers, json=data)

    if response.status_code == 409:
        logger.debug(f"Role {name} already exists in realm {realm_name}")
        return response.text
    if not response.raise_for_status():
        logger.debug(f"Created role {name}")
        return response.text


def create_realm_user(headers, realm_name, name, groups=None, attributes=None):
    if groups is None:
        groups = []
    if attributes is None:
        attributes = {}
    data = {"enabled": True, "attributes": attributes, "groups": groups, "username": name, "emailVerified": ""}
    response = requests.post(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/users", headers=headers, json=data)

    if response.status_code == 409:
        logger.debug(f"User {name} already exists in realm {realm_name}")
        return response.text
    if not response.raise_for_status():
        logger.debug(f"Created user {name}")
        return response.text


def get_user_by_name(headers, realm_name, name):
    # GET "{{keycloak_url}}/auth/admin/realms/{{realm}}/users/?username={{username}}"
    response = requests.get(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/users?username={name}", headers=headers)
    if not response.raise_for_status():
        return response.json()[0]


def get_role_by_name(headers, realm_name, name):
    # GET /{realm}/clients/{id}/roles/{role-name}
    response = requests.get(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/roles/{name}", headers=headers)
    if not response.raise_for_status():
        logger.debug(response.json())
        return response.json()


def add_role_to_user(headers, realm_name, userid, role):
    # /auth/admin/realms/myrealm/users/6f189f81-3757-4c59-9f99-06116b6a5e74/role-mappings/realm
    response = requests.post(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/users/{userid}/role-mappings/realm", headers=headers, json=[role])
    if response.status_code == 409:
        logger.debug(f"Client already has role {role}")
    if not response.raise_for_status():
        logger.debug(f"Role {role} added to user {userid}")


def get_users(headers, realm_name):
    response = requests.get(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/users", headers=headers)
    if not response.raise_for_status():
        return response.json()


def get_roles_by_user(headers, realm_name, userid):
    #GET /admin/realms/{realm}/users/{id}/role-mappings
    response = requests.get(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/users/{userid}/role-mappings", headers=headers)
    if not response.raise_for_status():
        return response.json()


def get_effective_roles_by_user(headers, realm_name, userid):
    # GET /admin/realms/{realm}/users/{id}/role-mappings/realm/composite
    response = requests.get(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/users/{userid}/role-mappings/realm/composite", headers=headers)
    if not response.raise_for_status():
        return response.json()


def get_effective_client_roles_by_user(headers, realm_name, client_name, userid):
    #GET /admin/realms/{realm}/clients/{id}
    #http://localhost:8080/auth/admin/realms/myrealm/clients?clientId=client&first=0&max=20&search=true
    response = requests.get(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/clients?clientId={client_name}", headers=headers)
    clientid = None
    if not response.raise_for_status() and len(response.json()) > 0:
        clientid = response.json()[0]['id']
    # GET /admin/realms/{realm}/users/{id}/role-mappings/realm/composite
    response = requests.get(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/users/{userid}/role-mappings/clients/{clientid}/composite", headers=headers)
    if not response.raise_for_status():
        return response.json()


def get_groups_by_user(headers, realm_name, userid):
    # GET /auth/admin/realms/myrealm/users/2646d40c-2842-4e84-bc26-8b5944d91ad1/groups
    response = requests.get(url=f"{keycloak_server}/auth/admin/realms/{realm_name}/users/{userid}/groups?briefRepresentation=false", headers=headers)
    if not response.raise_for_status():
        return response.json()

