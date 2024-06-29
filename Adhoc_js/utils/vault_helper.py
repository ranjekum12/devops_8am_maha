import os
import hvac
import logging
from .error_handling import log_error_and_raise_exception

def establish_connection():
    """
    establishes connection with the CST Vault service
    """
    global vault
    vault_addr = 'https://vault-amer.adobe.net'
    
    try:
        vault = hvac.Client(vault_addr)
        logging.info('Established connection to CST Vault')
    except Exception as exception:
        log_error_and_raise_exception('Establishing connection with CST Vault failed', exception)
    
    if 'VAULT_TOKEN' in os.environ:
        vault.token = os.environ['VAULT_TOKEN']
    else:
        log_error_and_raise_exception("'VAULT_TOKEN' environment variable has not been set")

    try:
        logging.debug("checking if vault is authenticated properly...")
        vault.is_authenticated()
    except Exception as exception:
        log_error_and_raise_exception('Authentication check with CST Vault failed', exception)
    
    return vault

def get_path_for_secret(secret_name: str) -> str:
    """
    returns the path for secret stored on vault
    """
    secret_base_path = 'secret/campaign/techops-secrets/campaign-ims/user-migration'
    secret_names = ['ims_access_token', 'ims_client_secret', 'ims_client_code', 'ims_client_id']

    if secret_name in secret_names:
        return f'{secret_base_path}/{secret_name}'
    
    log_error_and_raise_exception("Invalid secret name provided")

def read_secret(secret_name: str) -> str:
    """
    read a secret from vault
    """
    try:
        vault_client = establish_connection()

        secret_path = get_path_for_secret(secret_name)
        
        if vault_client:
            response = vault_client.read(secret_path)
            
            if response and ('data' in response) and ('secret' in response['data']):
                return response['data']['secret']
    except Exception as exception:
        log_error_and_raise_exception('Unable to read secret from vault', exception)

def write_secret(secret_name: str, secret_value: str):
    """
    write a secret on vault
    """
    try:
        vault_client = establish_connection()

        secret_path = get_path_for_secret(secret_name)
        
        if vault_client:
            vault_client.write(secret_path, secret=secret_value)
    except Exception as exception:
        log_error_and_raise_exception('Unable to write secret to vault')
