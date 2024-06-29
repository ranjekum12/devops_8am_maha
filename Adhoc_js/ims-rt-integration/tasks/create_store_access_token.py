import hvac
import requests
import logging
from utils.vault_helper import read_secret, write_secret
from utils.error_handling import log_error_and_exit, log_error_and_raise_exception

def read_client_secrets():
    """
    retrieves ims client secret, code and client id from vault
    """
    try:
        secrets = []

        secrets.append(read_secret('ims_client_secret'))
        secrets.append(read_secret('ims_client_code'))
        secrets.append(read_secret('ims_client_id'))
        
        return secrets
    except Exception as exception:
        log_error_and_raise_exception("Error retrieving secret from Vault", exception)

def generate_ims_access_token():
    """
    generates the ims access token
    """
    try:
        api_url = 'https://ims-na1.adobelogin.com/ims/token/v1'
        client_secret, code, client_id = read_client_secrets()
        payload = f"client_secret={client_secret}&code={code}&client_id={client_id}&grant_type=authorization_code"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
        }
        response = requests.post(api_url, data=payload, headers=headers)
        if response.status_code != 200:
            raise Exception("authentication failure %d" % (response.status_code))
        token = response.json().get('access_token')
        return token
    except Exception as exception:
        log_error_and_raise_exception("Error calling IMS API", exception)

def create_store_access_token():
    try:
        access_token = generate_ims_access_token()
        write_secret('ims_access_token', access_token)
    except Exception as exception:
        log_error_and_exit('Exception encountered in create_store_access_token task', exception)

def main():
    logging.basicConfig(level=logging.INFO)
    create_store_access_token()

if __name__ == "__main__":
    main()
