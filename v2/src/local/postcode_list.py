import logging
import argparse
import time
import os
import sys

from collections import defaultdict
from logging.handlers import RotatingFileHandler
from model.decoder import mapping_postcode as decoder

log = logging.getLogger("purple.v2.src.local.postcode_list")
#------------------------------------------------------------------------------
def controller():
    """
        Orchestrate the process from the command line agrs.

        Args:
            return: None
    """
    log.info("-------------------------------------------------------------------")
    start_exec = time.time()
    latest = 'http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv'
    log.debug(f'executing from path {os.getcwd()}')

    args = ParseCommandLine()
    if args.webfull is True:
        data_path = latest
        from ukio.http_reader import stream_file as rdr
    else:
        data_path = args.localfile
        from ukio.file_reader import stream_file as rdr
        
    num = save_postcode_list(rdr, data_path)
    log.info(f"Total records processed = {num}.")

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    print(f"Finished process (hours): {hours}:{mins}:{round(secs, 2)}.")
    log.info(f"Finished process: {hours}:{mins}:{round(secs, 2)}.")

#------------------------------------------------------------------------------
def save_postcode_list(reader, data_path):
    """
        Read the required file, decode the records to extract all postcodes.
        Save the postcodes to an Azure Table.

        Args:
            reader: either an http stream reader or a local file reader function
            data_path: the full location of the file (web url or file path)
            decoder: a function that retrieves a postcode from the a record
            return: Count of records processed
    """
    postcodes = defaultdict(set)
    count = 0
    total = 0

    for file_rec in reader(data_path):
        count += 1
        rec = decoder(file_rec)

        if len(rec['Postcode']) > 0:
            pc = rec['Postcode']
            oc = rec['Postcode'].split()[0]
            postcodes[oc].add(pc)

    for k, v in postcodes.items():
        if k == 'LS4':
            #pc_list = [{'Postcode':x} for x in v]
            total += len(v)
            log.info(f"{v} = {total}")
            
    return count

#---------------------------------------------------------------------------------------#
def ParseCommandLine():
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
            RotatingFileHandler('postcode_list.log', maxBytes=5242880, backupCount=10)
        ]
    )

    controller()