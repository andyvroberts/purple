import time
import logging
import ast
from collections import defaultdict
import azure.functions as func

from utils import http_reader
from utils import storage_queue
from utils import storage_blob
from utils import common

# ---------------------------------------------------------------------------------------#


def read_file_and_check_config():
    record_count = 0
    queue_count = 0
    vis_timeout = 0
    outcode_check = defaultdict(float)

    # get references for the storage clients
    qc = storage_queue.get_base64_queue_client(
        common.load_outcode_trigger_queue_name())
    bc = storage_blob.get_client(
        common.blob_container(), common.blob_file_name())

    config_str = storage_blob.read_config(bc)
    config = ast.literal_eval(config_str)

    for outcode, price in http_reader.stream_file_for_price_config():
        record_count += 1
        outcode_check[outcode] += price

    for k, v in outcode_check.items():
        if k in config:
            if v != config[k]:
                # outcode total value has changed so add to price-load trigger queue
                queue_count += 1
                vis_timeout = common.visibility_plus_30_secs(vis_timeout)
                storage_queue.send_message(qc, k, vis_timeout)
        else:
            # outcode not in config so add to price-load trigger queue
            queue_count += 1
            vis_timeout = common.visibility_plus_60_secs(vis_timeout)
            storage_queue.send_message(qc, k, vis_timeout)

    config_output = str(dict(outcode_check))
    storage_blob.store_config(bc, config_output)

    logging.info(f'OUTCODE_SCANNER. file records read = {record_count}')
    logging.info(
        f'OUTCODE_SCANNER. {qc.queue_name} Queue messages sent = {queue_count}')
    return record_count

# ---------------------------------------------------------------------------------------#


def main(outcodeScanner: func.TimerRequest) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger('azure.storage.queue').setLevel(logging.ERROR)

    rec_count = read_file_and_check_config()

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(
        f'OUTCODE_SCANNER. Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
