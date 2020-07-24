from datetime import datetime
import json

def getDefaultValueForText():
    return ""

def getDefaultValueForInt():
    return 0

def getDefaultVlaueForList():
    return []

def getDefaultValueForDict():
    return {}

def getDefaultValueForDate():
    return datetime.strftime(datetime.strptime('1970-01-01','%Y-%m-%d'),'%Y-%m-%dT%H:%M:%S.%fZ')

def getDefaultValueForTenantID():
    return '000000000000'

def getDefaultValueForDeviceID():
    return '00-00-00-00'

def post_error(errmsg):
    
    #construct the response with result
    response = {
        'statuscode':"585",
        'Message': errmsg,
        'dataToInsert': ""
        }
            
    #convert response to json format
    response = {
            "body": json.dumps(response)
            }
            
    return response
