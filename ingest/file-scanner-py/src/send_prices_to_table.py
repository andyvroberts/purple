import logging
import argparse
import time
import os
import sys

from operator import attrgetter
from collections import namedtuple, defaultdict

from logging.handlers import RotatingFileHandler
from azu import table_storage as tab
from model import formatter as fmt
from model import decoder as dcdr


log = logging.getLogger("purple.v2.src.local.send_prices_to_table")
#------------------------------------------------------------------------------
def controller():
    """
        Orchestrate the process from the command line args.
        1. Read the ready outcodes to process
        2. Scan the prices file for all postcode prices in the outcode
        3. format each postcode payload and load it into the prices table directly
        4. Mark the ready outcode as completed.

        Args: None
    """
    log.info("-------------------------------------------------------------------")
    start_exec = time.time()
    done = 0

    latest = 'http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv'
    log.debug(f'executing from path {os.getcwd()}')

    args = parse_command_line()
    if args.webfull is True:
        data_path = latest
        from ukio.http_reader import stream_file as rdr
    else:
        data_path = args.localfile
        from ukio.file_reader import stream_file as rdr

    outcode_client = tab.get_table_client("outcode")
    postcode_client = tab.get_table_client("prices")

    outcodes, postcodes = fetch_ready_postcodes(outcode_client)
    pc_list = fetch_prices(rdr, data_path, postcodes)
    sort_and_store(postcode_client, pc_list)
    done = deactivate_outcodes(outcode_client, outcodes)

    log.info(f"Completed {done} Outcodes.")

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    log.info(f"Finished process: {hours}:{mins}:{round(secs, 2)}.")


#---------------------------------------------------------------------------------------#
def fetch_ready_postcodes(cl1):
    """
        Read ready configuration rows to find the list of all Postcodes that will be used
        to look-up prices.

        Args:
            cl1: the azure table storage client for the 'outcode' table
            return: a tuple of distinct lists of outcodes and postcodes
    """
    postcodes = []
    outcodes = []

    for row in tab.query_ready_outcodes(cl1):
        outcodes.append(row['RowKey'])
        postcodes.extend(fmt.string_to_list(row['postcodes']))

    return outcodes, postcodes


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
    Price = namedtuple('Price', ['outcode', 'postcode', 'addresses'])
    all_prices = defaultdict(list)
    included_count = 0

    # read all postcodes and put into a list.
    for file_rec in reader(data_path):
        rec = dcdr.price_record(file_rec)
        pc = rec['Postcode']

        # for each postcode retrieve its price records
        if pc in postcodes:
            compact_rec = fmt.compact_price_rec(rec)
            all_prices[pc].append(compact_rec)
            included_count += 1

    log.info(f"Included {included_count} CSV price records.")
    return all_prices


#---------------------------------------------------------------------------------------#
def sort_and_store(cl2, postcode_list):
    """
        for each set of prices belonging to a single postcode, store in the table.

        Args:
            return: a list of postcodes
    """
    batch, batches, total = 0, 0, 0
    table_batch = []
    prev_outcode = 'no outcode'

    for k, v in sorted(postcode_list.items()):
        batch += 1
        new_outcode, table_rec = format_price_table_rec(k, v)
        log.debug(f"Previous outcode = {prev_outcode}, New Outcode = {new_outcode}. Current batch size: {len(table_batch)}.")

        if prev_outcode != new_outcode:
            if len(table_batch) > 0:
                total += tab.upsert_replace_batch(cl2, table_batch)
                table_batch = []
                batches += 1
                batch = 0
            prev_outcode = new_outcode

        table_batch.append(table_rec)

        if batch == 100:
            total += tab.upsert_replace_batch(cl2, table_batch)
            table_batch = []
            batches += 1
            batch = 0

    # insert the final entities that did not reach the batch limit
    if len(table_batch) > 0:
        total += tab.upsert_replace_batch(cl2, table_batch)
        batches += 1

    log.info(f"Inserted {batches} price table batches for {total} postcodes.")


# ---------------------------------------------------------------------------------------#
def format_price_table_rec(postcode, prices):
    """convert a list of postcode prices into a table record that can be stored
        Args:   
            postcode: the postcode of prices to be stored
            prices: one or more compact price records in a list
            Return: a storage table record
    """
    rec = {}

    outcode = postcode.split(' ')[0]
    entry = fmt.price_list_to_table_string(prices)
    
    rec['PartitionKey'] = outcode
    rec['RowKey'] = postcode
    rec['Addresses'] = entry

    return outcode, rec


#---------------------------------------------------------------------------------------#
def deactivate_outcodes(cl1, outcode_list):
    """
        Read ready configuration rows to find the list of all Postcodes that will be used
        to look-up prices.

        Args:
            cl1: the azure table storage client for the 'outcode' table
            postcodes: a list of outcodes and postcodes to deactivate
            return: Count of postcodes processed
    """
    updated_count = 0

    for oc in outcode_list:
        rec = {}
        rec['PartitionKey'] = 'OUTCODE'
        rec['RowKey'] = oc 
        rec['Status'] = 'D'
        tab.update(cl1, rec)
        updated_count += 1

    return updated_count


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
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s [%(name)s]: %(message)s",
        datefmt='%Y-%m-%d %I:%M:%S',
        handlers = [
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler('./send_prices_to_table.log', maxBytes=10240, backupCount=0)
        ]
    )

    controller()