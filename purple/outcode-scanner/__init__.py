import time
import logging
import azure.functions as func

from utils import http_reader
from utils import landreg_decoder
from utils import config_table

#---------------------------------------------------------------------------------------# 
def read_file_and_create_config(url, table_name):
    record_count = 0

    # always create the table and return the table service client.
    tc = config_table.create(table_name)

    for stream_rec in http_reader.stream_file(url):
        record_count += 1
        outcode = landreg_decoder.get_outcode(stream_rec)

        # if the outcode exists and is the one we are searching for.


    logging.info(f'File records read = {record_count}')
    return record_count


#---------------------------------------------------------------------------------------# 
def main(mytimer: func.TimerRequest) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    #logging.getLogger('azure.storage.queue').setLevel(logging.DEBUG)

    url1 = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv"
    url2 = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-2020.csv"
    
    rec_count = read_file_and_create_config(url1, "LandregConfig")

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(f'Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
