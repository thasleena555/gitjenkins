#name spaces
import json
import os
import requests
import logging
import utility

#logger object to log the status of pc status operation
logger			=	"" 

#max no of trials for posting the data into lms
no_of_trials	=	3 

#environment variable names of user credentials
logstashURL		=	""
userName		=	""
passwrd			=	""

#schema and stackname variables
schema_pc_info	=	""
stack_pc_info	=	""

#api which inserts the nas status  information in to logstash
def InsertPCStatusLogInfo(dataToInsert):
	try:
		
		#initialize default values
		SetUp()
		
		#assing schemaName and stackName before inserting the values 
		dataToInsert['schema']	=	schema_pc_info
		dataToInsert['stack']	=	stack_pc_info
		
		#remove operation type key before posting it to lms
		del dataToInsert['operationType']
		
		logger.info('PC status data for posting to LMS is :'+str(dataToInsert))
		
		#post to lms
		return PostDataToLMS(dataToInsert)
		
	except Exception as ex:
		return utility.post_error(str(ex))
		
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		return utility.post_error(errmsg)


#api initialize the requried objects and data for posting pcstatus to lms
def SetUp():

	try:
		#logger object initialization
		global logger
		logger	=	logging.getLogger()
		logger.setLevel(logging.INFO)
		
		#initialize the credentials
		#get logstash url, userName & password to insert values
		global logstashURL
		logstashURL		=	os.environ.get("endpoint")
		global userName
		userName		=	os.environ.get("username")
		global passwrd
		passwrd			=	os.environ.get("password")
		
		#read schema and stack values
		global schema_pc_info
		schema_pc_info		=	os.environ.get("schema_pc_info")
		global stack_pc_info
		stack_pc_info		=	os.environ.get("stack_pc_info")

	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		raise Exception(errmsg)    


#api which post pc status into lms
def PostDataToLMS(dataToInsert):
	try:
		#initialie default values
		result			=	""
		trial_index 	=	1

		#default content of headers
		req_headers     =  {
        	    "Content-type": "application/json"
        	}
	
		#loop for posting lms into logstash
		while(trial_index	<=	no_of_trials):
			
			#post to lms
			result	=	requests.post(logstashURL, data=json.dumps(dataToInsert), headers=req_headers, auth=(userName, passwrd))
			
			#increase trial_index to repeaat the loop if data fails to post
			trial_index		=	trial_index + 1 
			
			#validate for the result 
			#if posted successfully then stop looping else retry
			if (200	==	result.status_code):
				break

		
		#construct the response with result
		response    = {
			'statuscode'	:	result.status_code,
			'Message'		:	result.text
		}
			
		#convert response to json format
		response    = {
			"body"		:	json.dumps(response)
		}
			
		logger.info('response from LMS after posting :'+str(response))
		#return response to the caller
		return response
		
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		errmsg = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
		raise Exception(errmsg)    

		