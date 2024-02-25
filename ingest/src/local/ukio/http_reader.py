import logging
import requests

log = logging.getLogger("ukio.http_reader")
#---------------------------------------------------------------------------------------#   
def stream_file(url):
    """create a generator to stream-read HTTP file lines (records). 

        Args:
            path: the path to the data.
            Return: a generator of file records
    """
    log.info(f'Streaming price file from http {url}.')
    try:
        with requests.get(url, stream=True) as f:
            for line in f.iter_lines():
                if line:
                    csv_text = line.decode('utf-8')
                    yield csv_text

    except requests.RequestException as ex:
        log.error('Unable to load data from HTTP: {}'.format(ex))
        logging.shutdown()
        raise ex