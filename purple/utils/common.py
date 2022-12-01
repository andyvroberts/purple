""" 
    Some utility functions that return constants or formatted names of resources.
"""

#---------------------------------------------------------------------------------------# 
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

def visibility_plus_five_min(seconds):
    return 60 * 5 + seconds

def visibility_plus_30_secs(seconds):
    return 30 + seconds