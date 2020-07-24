
import json
import os
import requests
import datetime
import logging
import shlex
import pcstatuslog_function
import faxlog_function
import utility
import sys, traceback

logger =""

no_of_trials  = 3 #max no of trials for posting the data into lms
logstashURL = ""
userName = ""
passwrd  = ""
#initialize schemaname and stackname
schemaName_search = ""
schemaName_nas_info=""
stackName = ""

def setup():
  
  try:
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
  
    global logstashURL
    logstashURL = os.environ.get("endpoint")
    global userName
    userName = os.environ.get("username")
    global passwrd
    passwrd  = os.environ.get("password")
    #initialize schemaname and stackname
    global schemaName_search
    schemaName_search = os.environ.get("schema_search")
    global schemaName_nas_info
    schemaName_nas_info=os.environ.get("schema_nas_info")
    global stackName
    stackName = os.environ.get("stack_nas_info")
  except:
    # something went wrong while setting up
    logger.info("Error occurred while setup of fax log lambda")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
    raise Exception(errmsg)    

def nasagent_handler(event, context):
  try:
    
    setup()
    logger.info('event information is'+str(event))
    data=json.loads(event['body'])
    #data=event
    logger.info('nas agent body information is'+str(data))
    if data['operationType'] =='NASInformation':
      return InsertNasStatusLogInfo(data)
    if data['operationType'] =='WebSearch':
      return InsertOperationalLogInfo(data)
    if data['operationType'] =='pcstatus':
      return pcstatuslog_function.InsertPCStatusLogInfo(data)  
    if data['operationType'] =='FaxLog':
      return faxlog_function.InsertFaxLogInfo(data) 
    
    return utility.post_error('Invalid Operation TypeError')  
    
  except Exception as ex:
    return utility.post_error(str(ex))

def PostDataToLMS(dataToInsert):

  try:
    #initialie default values
    result = ""
    trial_index = 1
	
    req_headers =  {
            "Content-type": "application/json"
        }
	

    #loop for posting lms into logstash
    while (trial_index <= no_of_trials):
      result = requests.post(logstashURL, data=json.dumps(dataToInsert), headers=req_headers, auth=(userName, passwrd))
      trial_index = trial_index + 1 #increase trial_index to repeaat the loop if data fails to post
      #validate fof the result status code
      if (result.status_code == 200 ):
        break
    			
  	#construct the response with result
    response = {
		  'statuscode':result.status_code,
	  	'Message': result.text,
		  'dataToInsert':dataToInsert
		  }
			
    #convert response to json format
    response = {
			"body": json.dumps(response)
			}
			
    logger.info('response from LMS after posting :'+str(response))
    return response
  
  except:
    # something went wrong while setting up
    logger.info("Error occurred while setup of fax log lambda")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
    raise Exception(errmsg)  

def read_nasinfo_log_data(dataToInsert):
  try:
    #assing schemaName and stackName before inserting the values 
    dataToInsert['schema'] = schemaName_nas_info
    logger.info('schema for nas information is  is'+str(dataToInsert["schema"]))
    dataToInsert['stack'] = stackName
    logger.info('stack for nas information is  is'+str(dataToInsert["stack"]))
    #parsing disk space details 
    dataToInsert["avail_storage_size"]=int(dataToInsert["avail_storage_size"].split('M')[0]) if "avail_storage_size" in dataToInsert else utility.getDefaultValueForInt()
    dataToInsert["used_storage_size"]=int(dataToInsert["used_storage_size"].split('M')[0]) if "used_storage_size" in dataToInsert else utility.getDefaultValueForInt()
    logger.info('available storage space is'+str(dataToInsert["avail_storage_size"]))
    logger.info('used_storage_size is'+str(dataToInsert["used_storage_size"]))
    del dataToInsert['operationType']
    logger.info('final data for posting to LMS is :'+str(dataToInsert))
    return dataToInsert
  except:
    logger.info( "Error occurred in reading fax log data")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
    raise Exception(errmsg)
    
#api which inserts the nas status  information in to logstash
def InsertNasStatusLogInfo(dataToInsert):
  try:
    
    # code to read data
    dataToInsert=read_nasinfo_log_data(dataToInsert)
    logger.info('nas agent :'+str(dataToInsert))
    # code to send data to LMS
    response= PostDataToLMS(dataToInsert)
    logger.info("nas agent response " +str(response))
    return response
    
  except Exception as ex:
    return utility.post_error(str(ex))
   
#code to find count of keywords
def count_of_keywords(keyword,json_data):
  value=0
  try:
     if keyword in json_data and len(json_data[keyword])!=0 :
       if isinstance(json_data[keyword],list):
         value=len(json_data[keyword])
       else:
         value=len(shlex.split(json_data[keyword]))
  except (TypeError,ValueError,AttributeError) as e:
     logger.info('{0} error happend for {1} keyword in operational log'.format(e,keyword))
  return value    
        
    
#function to filter schema values           	
def read_operation_log_data(search_data_json):
  try:
    logger.info('operation log data for parsing before sending to LMS :'+str(search_data_json))
    # Getting data from input JSON
    if "input_search_param_hits" in search_data_json:
      input_search_param_hits = search_data_json["input_search_param_hits"]  
    else:
      return 
    logger.info('input search param hits  :'+str(input_search_param_hits))
    if "sdb_search_params" in input_search_param_hits:
      sdb_search_params=input_search_param_hits["sdb_search_params"]  
    else:
      return
    logger.info('sdb search params :'+str(sdb_search_params))
    # Setting data to output JSON
    operationLogData= {}
    operationLogData["tenant_id"]=search_data_json["tenant_id"] if "tenant_id" in  search_data_json else utility.getDefaultValueForTenantID()
    logger.info('tenant id  of operation log :'+str(operationLogData["tenant_id"]))
    operationLogData["nas_user_id"]=search_data_json["nas_user_id"] if "nas_user_id" in search_data_json and len(search_data_json["nas_user_id"])!=0 else utility.getDefaultValueForText()
    logger.info('nas user id  of operation log :'+str(operationLogData["nas_user_id"]))
    operationLogData["device_id"]=search_data_json["device_id"] if "device_id" in  search_data_json else utility.getDefaultValueForDeviceID()
    logger.info('device id  of operation log :'+str(operationLogData["device_id"]))
    operationLogData["log_time"]=search_data_json["log_time"] if "log_time" in search_data_json else utility.getDefaultValueForDate()
    logger.info('log time of operation log :'+str(operationLogData["log_time"]))
    operationLogData["operation_name"]= search_data_json["operation_name"] if "operation_name" in search_data_json else utility.getDefaultValueForText()
    logger.info('operation_name  of operation log :'+str(operationLogData["operation_name"]))
    if "operation_time" in search_data_json:
     operationLogData["operation_time"]=search_data_json["operation_time"]
    logger.info('operation_time  of operation log :'+str(operationLogData["operation_time"]))
    #0 if list doesn't exist or value is "".
    operationLogData["hits"]=int(search_data_json["hits"]) if "hits" in search_data_json and len(search_data_json["hits"]) !=0 else utility.getDefaultValueForInt()
    logger.info('hits  of operation log :'+str(operationLogData["hits"]))
    #keywords are separated by 1-byte space or 2-byte space.
    #There are a backslash as a escape for double quotation.
    #If multiple keywords are contained by double quotations, those keywords are considered to be one keyword.
    operationLogData["keyword_list"]=count_of_keywords("keyword_list",sdb_search_params)
    logger.info('keyword_list  of operation log :'+str(operationLogData["keyword_list"]))
    operationLogData["not_keyword_list"]=count_of_keywords("not_keyword_list",sdb_search_params)
    logger.info('not_keyword_list  of operation log :'+str(operationLogData["not_keyword_list"]))
    select_tag_list_count=len(sdb_search_params["select_tag_list"]) if "select_tag_list" in sdb_search_params and  len(sdb_search_params["select_tag_list"]) !=0 else 0
    operationLogData["select_word_list"]=count_of_keywords("select_word_list",sdb_search_params)+select_tag_list_count
    operationLogData["select_tag_list"]=utility.getDefaultVlaueForList()
    logger.info('select_word_list  of operation log :'+str(operationLogData["select_word_list"]))
    operationLogData["or_select_word_list"]=count_of_keywords("or_select_word_list",sdb_search_params)
    logger.info('or_select_word_list  of operation log :'+str(operationLogData["or_select_word_list"]))
    operationLogData["not_select_word_list"]=count_of_keywords("not_select_word_list",sdb_search_params) 
    operationLogData["target_filename_list"]=count_of_keywords("target_filename_list",sdb_search_params) 
    operationLogData["target_path_list"]=count_of_keywords("target_path_list",sdb_search_params)
    operationLogData["target_filetype_list"]= sdb_search_params["target_filetype_list"] if "target_filetype_list" in  sdb_search_params  and len(sdb_search_params["target_filetype_list"]) !=0 else utility.getDefaultVlaueForList()
    #Please do not specify this item if this item do not exist or value is "".
    if "min_size" in  sdb_search_params and sdb_search_params["min_size"]!="" :
      operationLogData["min_size"]=int(sdb_search_params["min_size"])
    if "max_size" in  sdb_search_params and sdb_search_params["max_size"]!="" :
      operationLogData["max_size"]=int(sdb_search_params["max_size"])
    if "start_date_create" in  search_data_json :
      operationLogData["start_date_create"]=search_data_json["start_date_create"]
    if "end_date_create" in  search_data_json:
      operationLogData["end_date_create"]=search_data_json["end_date_create"]
    if "start_date" in  search_data_json :
      operationLogData["start_date"]=search_data_json["start_date"]
    if "end_date" in  search_data_json :
       operationLogData["end_date"]=search_data_json["end_date"]
    if "start_date_entry" in  search_data_json:
      operationLogData["start_date_entry"]=search_data_json["start_date_entry"]
    if "end_date_entry" in  search_data_json :
      operationLogData["end_date_entry"]=search_data_json["end_date_entry"]
    if "start_date_shoot" in  search_data_json :
      operationLogData["start_date_shoot"]=search_data_json["start_date_shoot"]
    if "end_date_shoot" in  search_data_json:
      operationLogData["end_date_shoot"]=search_data_json["end_date_shoot"]
    operationLogData["creator_list"]=count_of_keywords("creator_list",sdb_search_params)
    operationLogData["updater_list"]=count_of_keywords("updater_list",sdb_search_params)
    if "min_page" in  sdb_search_params and sdb_search_params["min_page"]!="" :
      operationLogData["min_page"]=int(sdb_search_params["min_page"])
    if "max_page" in  sdb_search_params and sdb_search_params["max_page"]!="" :
      operationLogData["max_page"]=int(sdb_search_params["max_page"])
    if "from" in  sdb_search_params and sdb_search_params["from"]!="" :
      operationLogData["from"]=int(sdb_search_params["from"])
    if "size" in  sdb_search_params and sdb_search_params["size"]!="" :
      operationLogData["size"]=int(sdb_search_params["size"])
    if "sort_mode1" in  sdb_search_params and sdb_search_params["sort_mode1"]!="" :
       operationLogData["sort_mode1"]=int(sdb_search_params["sort_mode1"])
    if "sort_order1" in  sdb_search_params and sdb_search_params["sort_order1"]!="" :
       operationLogData["sort_order1"]=int(sdb_search_params["sort_order1"])
    if "sort_mode2" in  sdb_search_params and sdb_search_params["sort_mode2"]!="" :
       operationLogData["sort_mode2"]=int(sdb_search_params["sort_mode2"])
    if "sort_order2" in  sdb_search_params and sdb_search_params["sort_order2"]!="" :
       operationLogData["sort_order2"]=int(sdb_search_params["sort_order2"])
    if "creatorinfo_mode" in  sdb_search_params and sdb_search_params["creatorinfo_mode"]!="" :
       operationLogData["creatorinfo_mode"]=int(sdb_search_params["creatorinfo_mode"])
    if "pageinfo_mode" in  sdb_search_params and sdb_search_params["pageinfo_mode"]!="" :
       operationLogData["pageinfo_mode"]=int(sdb_search_params["pageinfo_mode"])
    # Add empty Array if list doesn't exist or target_filetype_list value is ""
    
    operationLogData["accept_path_list"]=sdb_search_params["accept_path_list"] if "accept_path_list" in sdb_search_params and len(sdb_search_params["accept_path_list"]) !=0 else utility.getDefaultVlaueForList()
    operationLogData["select_location_list"]=sdb_search_params["select_location_list"] if "select_location_list" in sdb_search_params and len(sdb_search_params["select_location_list"]) !=0 else utility.getDefaultVlaueForList()
    #assigning schemaName and stackName before inserting the values 
    operationLogData['schema'] = schemaName_search
    operationLogData['stack'] = stackName
    return operationLogData
  except:
    logger.info( "Error occurred in reading fax log data")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
    raise Exception(errmsg)
	
# function to sent operation log to LMS	
def InsertOperationalLogInfo(data):
  try:
    # code to read data
    dataToInserttoLogstash=read_operation_log_data(data)
   
    # code to send data to LMS
    response= PostDataToLMS(dataToInserttoLogstash)
    return response
  except Exception as ex:
    return utility.post_error(str(ex))

#commented code for future refernce
#API which inserts the data PCAgent log info into dynamodb
#import boto3 #boto3 is aws sdk to access aws service
#To handle errors
#from botocore.exceptions import ClientError
#def InsertLogDetailsInfoToDynamodb():
    
    #fetch the dynamodb resource
    #client = boto3.resource('dynamodb')
    #get the table
    #table = client.Table('ssp-agent-db-dbg')
    #code to post json data into dynamo db table
    #try:
    #    table.put_item(Item=item)
    #   result='Inserted successfully'
    #except ClientError as e:
    #    result=e.response['Error']['Message']
    #return success or an error message           
    #return json.dumps(result)
