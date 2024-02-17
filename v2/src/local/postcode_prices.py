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
    args = ParseCommandLine()
    cl = tab.get_table_client("outcode")

    if args.outcode is None:
        log.error(f"Missing outcode on execution")
        sys.exit(1)
    else:
        pass



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