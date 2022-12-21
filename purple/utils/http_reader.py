import logging
import requests
import csv
import os

# ---------------------------------------------------------------------------------------#


def stream_file():
    """create a generator to stream-read HTTP file lines (records). 
        https://2.python-requests.org/en/master/user/advanced/#id9
        Args:
            Return: a generator of tuples (outcode & price)
    """
    url = os.getenv('PriceDataURL')
    logging.info(f'Streaming price file from {url}.')
    try:
        with requests.get(url, stream=True) as f:
            for line in f.iter_lines():
                if line:
                    csv_text = line.decode('utf-8')
                    yield csv_text

    except requests.RequestException as ex:
        logging.error('Unable to load data from HTTP: {}'.format(ex))
        raise ex

# ---------------------------------------------------------------------------------------#


def stream_file_for_price_config():
    """create a generator to stream-read HTTP file lines (records). 
        https://2.python-requests.org/en/master/user/advanced/#id9
        Args:
            Return: a generator of tuples (outcode & price)
    """
    url = os.getenv('PriceDataURL')
    logging.info(f'Streaming price file from {url}.')
    try:
        with requests.get(url, stream=True) as f:
            for line in f.iter_lines():
                if line:
                    oc, pr = format_price_config(line.decode('utf-8'))
                    # ignore records without a populated postcode
                    if oc is not None:
                        yield oc, pr

    except requests.RequestException as ex:
        logging.error('Unable to load data from HTTP: {}'.format(ex))
        raise ex

# ---------------------------------------------------------------------------------------#


def stream_file_for_outcode(outcode):
    """create a generator to stream-read HTTP file lines (records). 
        https://2.python-requests.org/en/master/user/advanced/#id9
        Args:
            outcode: the outcode of records to return.
            Return: a generator of file records
    """
    url = os.getenv('PriceDataURL')
    logging.info(f'Streaming price file from {url}.')
    try:
        with requests.get(url, stream=True) as f:
            for line in f.iter_lines():
                if line:
                    csv_rec = format_price_rec(line.decode('utf-8'))
                    # ignore records without a populated postcode
                    if csv_rec is not None:
                        # filter just the outcode records we need.
                        if csv_rec['Postcode'].split(' ')[0].lower() == outcode:
                            yield csv_rec

    except requests.RequestException as ex:
        logging.error('Unable to load data from HTTP: {}'.format(ex))
        raise ex

# ---------------------------------------------------------------------------------------#


def format_address(paon, saon, street):
    """join the parts of the record that form the unique address component.
        Args:   
            paon, saon, street: strings representing components of address line 1
            Return: the address string
    """
    address_seq = []
    if paon:
        address_seq.append(paon)
    if saon:
        address_seq.append(saon)
    if street:
        address_seq.append(street)

    address_string = ' '.join(address_seq)
    return address_string

# ---------------------------------------------------------------------------------------#


def format_price_rec(rec):
    """format the csv record for storage in a queue message. 
        Args:   
            rec: a CSV string representing a data record of columns
            Return: a dictionary of the record to be added to the queue
    """
    in_cols = ['RowKey', 'Price', 'PriceDate', 'Postcode', 'PropertyType',
               'NewBuild', 'Duration', 'Paon', 'Saon', 'Street', 'Locality',
               'Town', 'District', 'County', 'PpdCategory', 'RecStatus']

    decoded_rec = csv.DictReader([rec], in_cols)
    price_rec = {}

    for cols in decoded_rec:
        if len(cols['Postcode']) > 0:
            price_rec['Postcode'] = cols['Postcode']
            price_rec['Address'] = format_address(
                cols['Paon'], cols['Saon'], cols['Street'])
            price_rec['Price'] = int(cols['Price'])
            price_rec['Date'] = cols['PriceDate'][0:10]  # yyyy-mm-dd only
            price_rec['Locality'] = cols['Locality']
            price_rec['Town'] = cols['Town']
            price_rec['District'] = cols['District']
            price_rec['County'] = cols['County']
            price_rec['RecStatus'] = cols['RecStatus']

        else:
            price_rec = None

    return price_rec

# ---------------------------------------------------------------------------------------#


def format_price_config(rec):
    """for CSV files, decode a single line that may be quote delimited with embedded 
       commas. Return the record as a dict with only the data you want.
        Args:   s
            rec: a CSV string representing a data record of columns
            Return: a tuple of the outcode and the property price
    """
    in_cols = ['RowKey', 'Price', 'PriceDate', 'Postcode', 'PropertyType',
               'NewBuild', 'Duration', 'Paon', 'Saon', 'Street', 'Locality',
               'Town', 'District', 'County', 'PpdCategory', 'RecStatus']

    decoded_rec = csv.DictReader([rec], in_cols)
    rec_outcode = None
    rec_price = 0

    for cols in decoded_rec:
        if len(cols['Postcode']) > 0:
            rec_price = int(cols['Price'])
            rec_outcode = cols['Postcode'].split(' ')[0].lower()

    return rec_outcode, rec_price
