import pandas as pd
import logging


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
    params = ['status', 'country', 'countryCode', 'city', 'timezone', 'lat', 'lon']
    params_string = ','.join(params)

    # create a dataframe to store the responses
    df_pd = pd.DataFrame(columns=['ip_address'] + params)

    # make the response for each of the IP addresses
    for ip in ip_address:
        resp = requests.get(url + ip, params={'fields': params_string})
        info = resp.json()
        logging.warning(f'Response: {info}')
        if info["status"] == 'success':
            # if response is okay, append to dataframe
            info = resp.json()
            info.update({'ip_address': ip})
            logging.warning(f'Response for IP: {ip} {info}')
            df_pd = df_pd._append(info, ignore_index=True)
        else:
            # if there was a problem with the response, trigger a warning
            logging.warning(f'Unsuccessful response for IP: {ip}')

    # return the dataframe with all the information
    return df_pd


if __name__ == "__main__":
    df = convert_ip_to_location_geoip(
        ip_address=['47.66.78.52', '47.45.67.52', '47.89.90.54'],
        params=['lat', 'lon', 'country', 'countryCode', 'city', 'timezone'])
    print(df.get('lat'))
    df.head()
