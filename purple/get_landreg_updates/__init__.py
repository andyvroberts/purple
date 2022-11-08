import time
import logging
import azure.functions as func

from utils import http_reader
from utils import landreg_decoder
from utils import storage_queue

#---------------------------------------------------------------------------------------# 
def read_and_decode(url):
    record_count = 0
    queue_count = 0
    code_set = set()
    queue_prefix = "landreg-"

    for stream_rec in http_reader.stream_file(url):
        record_count += 1
        rec = landreg_decoder.prune_rec_for_queue(stream_rec)

        if len(rec['Postcode']) > 0:
            outcode = queue_prefix + rec['Postcode'].split(' ')[0].lower()
            #pcode = rec['Postcode'].replace(' ','-').lower()
            if outcode not in code_set:
                code_set.add(outcode)
                storage_queue.create(outcode)

            storage_queue.send(outcode, rec)
            queue_count += 1

    logging.info(f'Distinct number of Queues = {len(code_set)}')
    logging.info(f'Messages sent = {len(queue_count)}')
    return record_count

#---------------------------------------------------------------------------------------# 
def main(mytimer: func.TimerRequest) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    #logging.getLogger('azure.storage.queue').setLevel(logging.DEBUG)

    url = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv"
    
    rec_count = read_and_decode(url)

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(f'Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
    logging.info(f'File record count = {rec_count}.')
