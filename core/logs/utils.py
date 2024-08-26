import random
import string
from datetime import datetime

from django.utils import timezone
from loguru import logger

import requests
import pandas as pd

from django.contrib.gis.geoip2 import GeoIP2


def convert_ip_to_location_geoip(ip_address=[], params=[]):
    # valid parameters to pass to the API
    valid_params = ['status', 'message', 'continenet', 'continentCode', 'country',
                    'countryCode', 'region', 'regionName', 'city', 'district',
                    'zip', 'lat', 'lon', 'timezone', 'offset', 'currency', 'isp',
                    'org', 'as', 'asname', 'reverse', 'mobile', 'proxy', 'hosting',
                    'query']
    # input checks
    assert isinstance(ip_address, list), 'The ip_address must be passed in a list'
    assert ip_address, 'You must pass at least one ip address to the function'
    assert isinstance(params, list), 'You must pass at least one parameter'
    for param in params:
        assert param in valid_params, f"{param} is not a valid parameter. List of valid params: {valid_params}"
    geo_ip = GeoIP2()

    result = geo_ip.city(ip_address[0])

    # specify query parameters we want to include in the response
    # and convert to properly formatted search string
    params = ['city', 'country_name', 'country_code', 'continent_name', 'timezone', 'latitude', 'longitude',
              'postal_code']

    # create a dataframe to store the responses
    df_pd = pd.DataFrame(columns=['ip_address'] + params)

    if result is not None:
        logger.warning(f'Response for IP - GeoIP2: {result}')
        df_pd = df_pd._append(result, ignore_index=True)
        return df_pd

    # return the dataframe with all the information
    logger.warning('NO response from GeoIP2 - Getting IP from ip-api.com...')
    return convert_ip_to_location(ip_address, params)


def convert_ip_to_location(ip_address=[], params=[]):
    '''
    This function takes a list of IP addresses, sends them to
    an API service and records the response which is associated
    with the location of the given IP address. A pd.DataFrame
    will be returned with all of the IP addresses and their
    location parameters.
    Parameters
    ----------
    ip_address: list[str]
        a list of the ip addresses that we want to send to the API
    params: list[str]
        a list of the parameters we would like to receive back from
        the API when we make our request
    Returns
    -------
    pd.DataFrame
        a pandas DataFrame that contains the original IP addresses as
        well as all of the location information retrieved for each from
        the API.
    '''

    # valid parameters to pass to the API
    valid_params = ['status', 'message', 'continenet', 'continentCode', 'country',
                    'countryCode', 'region', 'regionName', 'city', 'district',
                    'zip', 'lat', 'lon', 'timezone', 'offset', 'currency', 'isp',
                    'org', 'as', 'asname', 'reverse', 'mobile', 'proxy', 'hosting',
                    'query']

    # input checks
    assert isinstance(ip_address, list), 'The ip_address must be passed in a list'
    assert ip_address, 'You must pass at least one ip address to the function'
    assert isinstance(params, list), 'You must pass at least one parameter'
    for param in params:
        assert param in valid_params, f"{param} is not a valid parameter. List of valid params: {valid_params}"

    # the base URL for the API to connect to (JSON response)
    url = 'http://ip-api.com/json/'

    # specify query parameters we want to include in the response
    # and convert to properly formatted search string
    params = ['status', 'country', 'countryCode', 'city', 'timezone', 'lat', 'lon', 'zip']
    params_string = ','.join(params)

    # create a dataframe to store the responses
    df_pd = pd.DataFrame(columns=['ip_address'] + params)

    # make the response for each of the IP addresses
    for ip in ip_address:
        resp = requests.get(url + ip, params={'fields': params_string})
        info = resp.json()
        if info["status"] == 'success':
            # if response is okay, append to dataframe
            info = resp.json()
            info.update({'ip_address': ip})
            logger.warning(f'Response for IP: {ip} {info}')
            df_pd = df_pd._append(info, ignore_index=True)
        else:
            # if there was a problem with the response, trigger a warning
            logger.warning(f'Unsuccessful response for IP: {ip}')

    # return the dataframe with all the information
    return df_pd


def get_remote_address(request):
    for header in [
        "X-Real-Ip",
        "X-Forwarded-For",
        "Proxy-Client-IP",
        "WL-Proxy-Client-IP",
        "HTTP_CLIENT_IP",
        "HTTP_X_FORWARDED_FOR",
    ]:
        readdr = getattr(request, header, None)
        if readdr:
            logger.info(f"Your IP address is: {readdr}")
            return readdr


def get_client_ip_split(request):
    """
    This function retrieves the client's IP address by first checking for the 'HTTP_X_FORWARDED_FOR' header in the request's META dictionary.
    If it exists, it splits the header value by comma and returns the first part as the client's IP address.
    If 'HTTP_X_FORWARDED_FOR' is not present, it falls back to the 'REMOTE_ADDR' header.

    :param request: The HTTP request object.
    :return: The client's IP address as a string.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR", None)

    logger.info(f"Your IP address is: {ip}")
    return ip


def get_client_ip_from_request(request):
    """
    This function retrieves the client's IP address by first checking for the 'HTTP_X_FORWARDED_FOR' header in the request's META dictionary.
    If it exists, it falls back to the 'REMOTE_ADDR' header.

    :param request: The HTTP request object.
    :return: The client's IP address as a string.
    """
    for header in [
        "HTTP_X_FORWARDED_FOR",
        "REMOTE_ADDR",
        "X-Real-Ip",
        "X-Forwarded-For",
        "Proxy-Client-IP",
        "WL-Proxy-Client-IP",
        "HTTP_CLIENT_IP",
    ]:
        # Check for forwarded IP address from proxy
        remote_address = request.META.get(header, None)
        if remote_address:
            # Fallback to direct IP address if no forwarded IP
            logger.info(f"Your IP address is: {remote_address}")
            return remote_address

    logger.info("Unable to retrieve your IP address.")
    return None


def get_client_ip(request):
    """
    This function retrieves the client's IP address by first checking for the 'HTTP_X_FORWARDED_FOR' header in the request's META dictionary.
    If it exists, it falls back to the 'REMOTE_ADDR' header. If none of these headers contain an IP address, it falls back to the 'get_remote_address' function.

    :param request: The HTTP request object.
    :return: The client's IP address as a string.
    """
    raddress = get_client_ip_from_request(request)

    if raddress:
        return raddress
    else:
        raddress = get_client_ip_split(request)
        if raddress:
            return raddress
        else:
            raddress = get_remote_address(request)

    return raddress


def get_localdate():
    # datetime object containing current date and time
    now = timezone.now()

    # YY-mm-ddTHH:MM:SS
    dt_string = now.strftime("%Y-%m-%dT%HH:%MM:%SS")

    return dt_string


def get_localdate_dt():
    # datetime object containing current date and time
    now = timezone.now()

    return now


def get_id_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_uppercase
    result_str = "".join(random.choice(letters) for _ in range(length))
    now = datetime.now()
    now.strftime("%d")
    now.strftime("%m")
    now.strftime("%Y")
    now.strftime("%H")
    now.strftime("%M")
    return "%s%s%s%s%s%s" % (
        now.strftime("%d"),
        now.strftime("%m"),
        now.strftime("%Y"),
        now.strftime("%H"),
        now.strftime("%M"),
        result_str,
    )


if __name__ == "__main__":

    for header in [
        "X-Real-Ip",
        "X-Forwarded-For",
        "Proxy-Client-IP",
        "WL-Proxy-Client-IP",
        "HTTP_CLIENT_IP",
        "HTTP_X_FORWARDED_FOR",
    ]:
        print(header)
