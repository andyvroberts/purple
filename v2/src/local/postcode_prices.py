import logging
import argparse
import time
import os
import sys

from logging.handlers import RotatingFileHandler

from azu import table_storage as tab
from model import formatter as fmt
from model.decoder import mapping_postcode as decoder

log = logging.getLogger("purple.v2.src.local.postcode_prices")
#------------------------------------------------------------------------------
def controller():
    """
        Orchestrate the process from the command line agrs.

        Args:
            return: None
    """
    log.info("-------------------------------------------------------------------")
    start_exec = time.time()

    args = ParseCommandLine()
    cl = tab.get_table_client("outcode")

    for row in tab.query_ready_outcodes(cl):
        log.info(row)


    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    log.info(f"Finished process: {hours}:{mins}:{round(secs, 2)}.")


#---------------------------------------------------------------------------------------#
def ParseCommandLine():
    """Identify flags and values passed into execution
    """
    par = argparse.ArgumentParser('UK Land Data Loader: command line parser')
    par.add_argument('-u', '--outcode', required=False, help='load all prices for all postcodes within an outcode')
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