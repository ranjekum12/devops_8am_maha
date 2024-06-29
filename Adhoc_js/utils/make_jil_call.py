import requests
from typing import Optional, Dict
from .make_http_call import make_http_call
from .vault_helper import read_secret

def make_jil_call(api: str, status_map: Dict[int, str], access_token: str,
                  verb: str = "GET",
                  payload: Optional[Dict[str, str]] = None,
                  params: Optional[Dict[str, str]] = None) -> requests.Response:
    """
    JIL specific wrapper around the make_http_call function
    """
    jil_endpoint = 'https://bps-il.adobe.io/jil-api'
    api_key = read_secret('ims_client_id')

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'X-Api-Key': api_key
    }

    url = "{}/{}".format(jil_endpoint, api)

    return make_http_call(url, headers, status_map, verb, payload, params)
