""" 
    Some utility functions that return constants or formatted names of resources.
"""

#---------------------------------------------------------------------------------------# 
def config_table_name():
    return "LandregConfig"

def load_trigger_queue_name():
    return "load-outcodes"

def config_outcode_changes_partition():
    return "OutcodeChanges"

def format_landreg_resource_name(suffix):
    return "landreg_" + suffix

def config_ready_status():
    return "A"
