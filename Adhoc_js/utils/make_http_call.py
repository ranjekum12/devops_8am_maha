import requests
from typing import Optional, Dict
from time import sleep
from .error_handling import log_error_and_raise_exception
import logging

def make_http_call(url: str, headers: Dict[str, str], status_map: Dict[int, str],
                   verb: str = "GET", payload: Optional[Dict[str, str]] = None,
                   params: Optional[Dict[str, str]] = None, max_retries: int = 3) -> requests.Response:
    """
    Makes an HTTP call. 
    If the response status code is not present in the status map then the call is retried.
    If the response HTTP status code is 429, then we retry after 'retry-after header value' seconds.

    Args:
        url: The URL to make the HTTP call to.
        headers: A dictionary of headers to include in the HTTP request.
        status_map: A dictionary where the keys are HTTP status codes and the values are messages to print if that status
            code is received.
        verb: The HTTP verb to use (default is "GET").
        payload: An optional dictionary of data to include in the HTTP request body (default is None).
        params: An optional dictionary of URL parameters to include in the HTTP request (default is None).
        max_retries: The maximum number of retries to attempt for HTTP status code not in status map (default is 3).

    Returns:
        A requests.Response object containing the HTTP response.

    Raises:
        Exception in the following cases:
        1. Any internal exception raised when making the HTTP call
        2. Received unexpected HTTP status code i.e, status code not present in the status_map
        3. The number of retries exceed max_retries
    """
    try:
        retries = 0
        
        while retries <= max_retries:
            if verb == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif verb == "POST":
                response = requests.post(url, headers=headers, json=payload, params=params)
            else:
                log_error_and_raise_exception(f"Unsupported HTTP verb {verb}")

            if response.status_code in status_map:
                # If the status code is in the map, print the status message and return the response object
                logging.info(status_map[response.status_code])
                return response
            
            logging.warning(f"Received unexpected HTTP status code {response.status_code}")
            retries += 1

            if response.status_code == 429:
                # sleep based on Retry-After header
                retry_after = int(response.headers.get('Retry-After', '2'))
                sleep(retry_after)

        # number of retries exceeded max_retries, raise an exception
        log_error_and_raise_exception(f"Exceeded maximum number of retries '{max_retries}'")

    except Exception as exception:
        log_error_and_raise_exception(f"Exception encountered while making a HTTP {verb} call to url '{url}'", exception)
