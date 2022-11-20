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

def config_ready_status():
    return "A"

def landreg_monthly_update_url():
    return "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv"

def landreg_yearly_url(year):
    base_name = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-XXXX.csv"
    file_url = base_name.replace('XXXX', year)
    return file_url
