import os

""" 
    Some utility functions that return constants or formatted names of resources.
"""


def get_data_url():
    env_url = os.getenv('PriceDataURL')
    env_year = os.getenv('PriceDataYear')
    url = env_url.replace('XXXX', env_year)
    return url


def config_table_name():
    return "LandregConfig"


def price_table_name():
    return "LandregPrice"


def load_outcode_trigger_queue_name():
    return "load-outcodes"


def load_postcode_trigger_queue_name():
    return "load-postcodes"


def config_outcode_changes_partition():
    return "OutcodeChanges"


def format_landreg_queue_name(suffix):
    return "landreg-" + suffix


def format_landreg_resource_name(suffix):
    return "landreg_" + suffix


def blob_container():
    return "landreg"


def blob_file_name(year):
    return f"outcode-config-{year}.txt"


def visibility_plus_30_secs(seconds):
    return 30 + seconds


def visibility_plus_60_secs(seconds):
    return 60 + seconds
