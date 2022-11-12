import logging
import requests

#---------------------------------------------------------------------------------------#   
def stream_file(url):
    """create a generator to stream-read HTTP file lines (records). 
        https://2.python-requests.org/en/master/user/advanced/#id9
        Args:
            path: the path to the data.
            Return: a generator of file records
    """
    logging.info(f'Streaming price file from {url}.')
    try:
        with requests.get(url, stream=True) as f:
            for line in f.iter_lines():
                if line:
                    csv_text = line.decode('utf-8')
                    yield csv_text

    except requests.RequestException as ex:
        logging.error('Unable to load data from HTTP: {}'.format(ex))
        raise ex
    