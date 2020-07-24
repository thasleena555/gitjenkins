
import json
import os
import requests
from datetime import datetime
import logging
import utility
import sys, traceback

logger = ""


logstashURL = ""
userName = ""
passwrd  = ""

schemaName = ""
stackName = ""

#max no of trials for posting the data into lms
no_of_trials  = 3 

def setup():

	try:

		# setup logger
		global logger
		logger = logging.getLogger()
		logger.setLevel(logging.INFO)
		
		#get logstash url, userName & password to insert values
		global logstashURL 
		logstashURL = os.environ.get("endpoint")
		global userName 
		userName = os.environ.get("username")
		global passwrd  
		passwrd  = os.environ.get("password")
		
		#initialize schemaname and stackname
		global schemaName 
		schemaName = os.environ.get("schema_fax")
		global stackName 
		stackName = os.environ.get("stack_fax")
		
		return True
		
	except:
		# something went wrong while setting up
		logger.info("Error occurred while setup of fax log lambda")
		exc_type, exc_value, exc_traceback = sys.exc_info()
		errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		raise Exception(errmsg)




# code to post data to LMS
def PostDataToLMS(dataToInsert):

	try:
		
		#initialie default values
		result = ""
		trial_index = 1
		
		req_headers =  {
				"Content-type": "application/json"
			}
		
		#loop for posting lms into logstash
		while(trial_index <= no_of_trials):
			result = requests.post(logstashURL, data=json.dumps(dataToInsert), headers=req_headers, auth=(userName, passwrd))
			trial_index = trial_index + 1 
			
			#increase trial_index to repeaat the loop if data fails to post
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
		logger.info("Error occurred while posting FAX log to LMS")
		exc_type, exc_value, exc_traceback = sys.exc_info()
		errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		raise Exception(errmsg)

# code to read fax data
def read_fax_log_data(data):

	try:
		
		dataToInserttoLogstash= {}

		#assigning schemaName and stackName before inserting the values 
		dataToInserttoLogstash['schema'] = schemaName
		dataToInserttoLogstash['stack'] = stackName
		logger.info('schema of FAX log :'+str(schemaName))
		logger.info('stack of FAX log :'+str(stackName))
	
		dataToInserttoLogstash['tenant_id']=data['tenant_id'] if 'tenant_id' in data else utility.getDefaultValueForTenantID()
		dataToInserttoLogstash['device_id']=data['device_id'] if 'device_id' in data else utility.getDegetDefaultValueForDeviceIDfaultDeviceID()
		
		dataToInserttoLogstash['user_id']=data['user_id'] if 'user_id' in data else utility.getDefaultValueForText()
		logger.info('user_id of fax log:'+str(dataToInserttoLogstash["user_id"]))
		
		dataToInserttoLogstash["user_name"]=data["user_name"] if "user_name" in data else utility.getDefaultValueForText()
		logger.info('user_name of fax log:'+str(dataToInserttoLogstash["user_name"]))
		
		dataToInserttoLogstash['operation']=data['operation'] if 'operation' in data else utility.getDefaultValueForText()
		logger.info('operation of fax log:'+str(dataToInserttoLogstash['operation']))

		dataToInserttoLogstash['operation_detail']=data['operation_detail'] if 'operation_detail' in data else utility.getDefaultValueForText()
		logger.info('operation_detail of fax log:'+str(dataToInserttoLogstash['operation_detail']))

		dataToInserttoLogstash['logoutput_time']=data["logoutput_time"]  if 'logoutput_time' in data else utility.getDefaultValueForDate()
		logger.info('logoutput_time of fax log:'+str(dataToInserttoLogstash['logoutput_time']))

		dataToInserttoLogstash['operation_time']=data["operation_time"] if "operation_time" in data else  utility.getDefaultValueForDate()
		logger.info('operation_time of fax log:'+str(dataToInserttoLogstash['operation_time']))

		dataToInserttoLogstash['mfp_device_id']=data['mfp_device_id'] if 'mfp_device_id' in data else utility.getDefaultValueForText()
		logger.info('mfp_device_id of fax log:'+str(dataToInserttoLogstash['mfp_device_id']))

		dataToInserttoLogstash['mfp_device_type']=data['mfp_device_type'] if 'mfp_device_type' in data else utility.getDefaultValueForText()
		logger.info('mfp_device_type of fax log:'+str(dataToInserttoLogstash['mfp_device_type']))

		dataToInserttoLogstash['re_file_type']=data['re_file_type'] if 're_file_type' in data else utility.getDefaultValueForText()
		logger.info('re_file_type of fax log:'+str(dataToInserttoLogstash['re_file_type']))

		dataToInserttoLogstash['re_file_size']=data['re_file_size'] if 're_file_size' in data else utility.getDefaultValueForInt()
		logger.info('re_file_size of fax log:'+str(dataToInserttoLogstash['re_file_size']))

		dataToInserttoLogstash['re_file_num']=data['re_file_num'] if 're_file_num' in data else utility.getDefaultValueForInt()
		logger.info('re_file_num of fax log:'+str(dataToInserttoLogstash['re_file_num']))

		dataToInserttoLogstash['se_file_type']=data['se_file_type'] if 'se_file_type' in data else utility.getDefaultValueForText()
		logger.info('se_file_type of fax log:'+str(dataToInserttoLogstash['se_file_type']))

		dataToInserttoLogstash['se_file_size']=data['se_file_size'] if 'se_file_size' in data else utility.getDefaultValueForInt()
		logger.info('se_file_size of fax log:'+str(dataToInserttoLogstash['se_file_size']))

		dataToInserttoLogstash['se_file_num']=data['se_file_num'] if 'se_file_num' in data else utility.getDefaultValueForInt()
		logger.info('se_file_num of fax log:'+str(dataToInserttoLogstash['se_file_num']))

		dataToInserttoLogstash['phone_number']=data['phone_number'] if 'phone_number' in data else utility.getDefaultValueForText()
		logger.info('phone_number of fax log:'+str(dataToInserttoLogstash['phone_number']))

		dataToInserttoLogstash['address']=data['address'] if 'address' in data else utility.getDefaultValueForText()
		logger.info('address of fax log:'+str(dataToInserttoLogstash['address']))
		logger.info('final fax log data is sending to LMS :'+str(dataToInserttoLogstash))
		
		return dataToInserttoLogstash
	
	except:
		logger.info( "Error occurred in reading fax log data")
		exc_type, exc_value, exc_traceback = sys.exc_info()
		errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		raise Exception(errmsg)

# code for fax logs
def InsertFaxLogInfo(data):

	try:
		setup()
		# code to read data
		dataToInserttoLogstash = read_fax_log_data(data)
		# code to send data to LMS
		response = PostDataToLMS(dataToInserttoLogstash)
		return response

	except Exception as ex:
		logger.info("Error occurred in Fax log main function")
		return utility.post_error(str(ex))
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		return utility.post_error(errmsg)
