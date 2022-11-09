import requests
import logging
import sys
import os
import time
import argparse
import csv
from collections import defaultdict


#---------------------------------------------------------------------------------------#   
def controller() -> None:
    """
        Read each record in the csv file and accumulate a count for each distinct 
        outcode that is found.

        Args: None
    """
    log = logging.getLogger("outcode_counter.controller")
    log.info("-------------------------------------------------------------------")
    start_exec = time.time()
    log.debug(f'executing from path {os.getcwd()}')

    args = parse_command_line()
    data_url = args.url

    # collect the count by outcode
    outcodes = defaultdict(int)
    for csv_row in stream_file(data_url):
        if len(csv_row['Postcode']) > 0:
            oc = csv_row['Postcode'].split(' ')[0].upper()
            outcodes[oc] += 1


    # sort the values (item[1]) in the default descending order.
    srt = {k: v for k, v in sorted(outcodes.items(), key=lambda item: item[1])}

    # log the output
    for k, v in srt.items():
        log.info(f'{k}: {v:,}')

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    log.info(f"Finished process: {hours}:{mins}:{round(secs, 2)}.")


#---------------------------------------------------------------------------------------#   
def stream_file(url):
    log = logging.getLogger("outcode_counter.stream_file")
    try:
        with requests.get(url, stream=True) as f:
            for line in f.iter_lines():
                if line:
                    csv_text = line.decode('utf-8')
                    yield decode(csv_text)

    except requests.RequestException as ex:
        logging.error('Unable to load data from HTTP: {}'.format(ex))
        raise ex


#---------------------------------------------------------------------------------------#
def decode(rec):
    """
        for CSV files, decode a single line that may be quote delimited with embedded 
        commas. Return the record as a dict

        Args:   
            rec: a CSV string representing a data record of columns
            Return: the dict of needed column names and values
    """
    in_cols = ['RowKey','Price','PriceDate','Postcode','PropertyType',\
               'NewBuild','Duration','Paon','Saon','Street','Locality',\
               'Town','District','County','PpdCategory','RecStatus']
    
    out_cols = ['Price','PriceDate','Postcode',\
                'Paon','Saon','Street','Locality',\
                'Town','District','County']

    decoded_rec = csv.DictReader([rec], in_cols)
    in_dict = next(decoded_rec).copy()
    out_dict = {k : v for k,v in filter(lambda t: t[0] in out_cols, in_dict.items())}

    return out_dict


#------------------------------------------------------------------------------
def parse_command_line():
    par = argparse.ArgumentParser("Land Registry data file - outcode counter")
    par.add_argument('-u', '--url', required=True, help='the full web url of the land registry file')

    args = par.parse_args()
    return args


#------------------------------------------------------------------------------
if __name__ == '__main__' :
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s [%(name)s]: %(message)s",
        datefmt='%Y-%m-%d %I:%M:%S',
        handlers = [
            logging.StreamHandler(sys.stdout)
        ]
    )
    controller()

#
# py outcode_counter.py -u "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv"
# py outcode_counter.py -u "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-2019.csv"
# 