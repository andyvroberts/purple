import logging
import argparse
import time
import os
import sys

from collections import defaultdict
from logging.handlers import RotatingFileHandler
from azu import table_storage as tab
from model import formatter as fmt
from model import decoder as dcdr


log = logging.getLogger("purple.v2.src.local.postcode_prices")
#------------------------------------------------------------------------------
def controller():
    """
        Orchestrate the process from the command line args.

        Args: None
    """
    log.info("-------------------------------------------------------------------")
    start_exec = time.time()

    latest = 'http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv'
    log.debug(f'executing from path {os.getcwd()}')

    args = parse_command_line()
    if args.webfull is True:
        data_path = latest
        from ukio.http_reader import stream_file as rdr
    else:
        data_path = args.localfile
        from ukio.file_reader import stream_file as rdr

    args = parse_command_line()
    pc_list = fetch_prices(rdr, data_path, fetch_ready_postcodes())

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    log.info(f"Finished process: {hours}:{mins}:{round(secs, 2)}.")


#---------------------------------------------------------------------------------------#
def fetch_ready_postcodes():
    """
        Read ready configuration rows to find the list of all Postcodes that will be used
        to look-up prices.

        Args:
            return: a list of postcodes
    """
    postcodes = []
    cl = tab.get_table_client("outcode")

    for row in tab.query_ready_outcodes(cl):
        postcodes.extend(fmt.string_to_list(row['postcodes']))

    return postcodes


#---------------------------------------------------------------------------------------#
def fetch_prices(reader, data_path, postcodes):
    """
        Read the input price file and for each 'ready' postcode, accumulate an array
        of price records.

        Args:
            reader: either an http stream reader or a local file reader function
            data_path: the full location of the file (web url or file path)
            postcodes: a list of postcodes for the price records to fetch
            return: Count of records processed
    """
    all_prices = defaultdict(set)

    # read all postcodes and put into a list.
    for file_rec in reader(data_path):
        rec = dcdr.price_record(file_rec)
        pc = rec['Postcode']

        # for each postcode retrieve its price records
        if pc in postcodes:
            compact_rec = fmt.compact_price_rec(rec)
            all_prices[pc].add(compact_rec)

    # for k, v in all_prices.items():
    #     log.info(f"Postcode = {k}")
    return all_prices


#---------------------------------------------------------------------------------------#
def group_and_push(postcode_set):
    """
        for each set of prices belonging to a single postcode, create a queue message

        Args:
            return: a list of postcodes
    """
    postcodes = []
    cl = tab.get_table_client("outcode")

    for row in tab.query_ready_outcodes(cl):
        postcodes.extend(fmt.string_to_list(row['postcodes']))

    return postcodes


#---------------------------------------------------------------------------------------#
def parse_command_line():
    """Identify flags and values passed into execution
    """
    par = argparse.ArgumentParser('UK Land Data Loader: command line parser')
    par.add_argument('-f', '--webfull', const=True, default=False, nargs='?', help='Full web file load flag')
    par.add_argument('-l', '--localfile', required=False, help='load a file from the local file system')
    args = par.parse_args()
    return args


#------------------------------------------------------------------------------
if __name__ == '__main__' :
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s [%(name)s]: %(message)s",
        datefmt='%Y-%m-%d %I:%M:%S',
        handlers = [
            logging.StreamHandler(sys.stdout), 
            RotatingFileHandler('postcode_prices.log', maxBytes=5242880, backupCount=10)
        ]
    )

    controller()