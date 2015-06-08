#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 15-Jan-10

#This module provide a fascade fauction on pycurl.
#you just need to pass some parameters to the function, and it does it all!



import os, atexit
import sys
import pycurl, json
from io import BytesIO


app_path = os.path.dirname(__file__)
sys.path.append(app_path)

if app_path:
    os.chdir(app_path)
else:
    app_path = os.getcwd()



#USAGE:
'''
url= '10.1.48.25:5000/v3/projects'
request = {"project": {"description": desc , "enabled": True , "name": name }}
header_list = ['Content-Type: application/json', 'Accept: application/json'] # ['header: value']
result = curl (url, header_list, '201', 'POST', request)
'''

def curl(url, headers_list, response_code, method, req = None):

    """
    Send a CURL request to specified URL. it prints Error Message (if the message is sent but returned some errors) 
    @type url: string
    @param url: URL of web server
    @type headers_list: stirng
    @param headers_list: list of HTTP header. each entry is a string in the following format: 'header: value'
    @type response_code: string
    @param response_code: accepted response code. if the web server returns another response_code there are some errors
    @type method: stirng
    @param method: HTTP Methods. it Includes: GET, POST, DELETE, PUT, PATCH   
    @type request: Dictionary
    @param request: a dictionary of resqest which will be convert to json and send to server.
    @rtype: boolean OR String
    @return: it retruns a dictionary of the form {"status": "error/success", "message": "errormessage/responsedataInJson/None"}, in case of errors, it prints the error
    """
    #print "curl.."

    data = BytesIO()        
    headers = BytesIO()        
    curlObj = pycurl.Curl()
    request = json.dumps(req).encode('UTF-8')    

    curlObj.setopt(pycurl.URL, url)
    curlObj.setopt(pycurl.HTTPHEADER,headers_list)

    if method == 'DELETE':
        curlObj.setopt(pycurl.CUSTOMREQUEST,'DELETE')
    elif method == 'POST':
        curlObj.setopt(pycurl.POSTFIELDS,request)
    elif method == 'GET':
        pass
    elif method == 'PUT':
        curlObj.setopt(pycurl.CUSTOMREQUEST,'PUT')
        if request is not None: 
            curlObj.setopt(pycurl.POST,1)
            curlObj.setopt(pycurl.POSTFIELDS,request)
    else :
        print "Curl: Unkown http method....", method
        return {"status":"error", "message":"Unkown http method"}

    """
    elif method == 'PATCH':
        print "PATCH PART"
        return True
    """

    curlObj.setopt(pycurl.WRITEFUNCTION,data.write)
    curlObj.setopt(pycurl.HEADERFUNCTION,headers.write)

    try :
        curlObj.perform()
    except Exception as e:
        print "Excteption occured in curl : ", str(e)
	return {"status":"error", "message":"Excteption occured in curl : " + str(e)}
	#return False
    curlObj.close()

        
    #status_code = curlObj.getinfo(pycurl.HTTP_CODE)    
    if headers.getvalue() is None :
	print "Curl: Error: No value in header"
	return {"status":"error", "message":"Header in response is None"}
	#return False


    if response_code in headers.getvalue().splitlines()[0] :
        if data.getvalue() :#is not None OR is not False
 	    return {'status':'success', 'message':json.loads(data.getvalue())}
            #return json.loads(data.getvalue())
        else :
            #return True
	    return {'status':'success', 'message':''} #OR {'message':None} 
    else :
	print "\n"
 	print "^^^^^^^^^^^^^^^^^  Curl Error...^^^^^^^^^^^^^^^^^^^"
        print "HEADERS: ",headers.getvalue() #.splitlines()[0] to print only the first line
        x=json.loads(data.getvalue())
        print "DATA: ",data.getvalue()
	print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
	print "\n"

        if "error" in x.keys() :
            #print "Error message : ", x["error"]["message"]
	    return {'status':'error' ,'message': x["error"]["message"]}
        #elif "Bad request" in x.keys() :
        elif "badRequest" in x.keys() :
            #print "Error message : ", x["badRequest"]["message"]
	    return {'status': 'error', 'message':'badRequest: '+ x["badRequest"]["message"]}
	elif "NeutronError" in x.keys() :
            return {'status': 'error', 'message':'NeutronError: '+ x["NeutronError"]["message"]}
        return {'status': 'error', 'message': 'An unspecified error occured in curl. One may like to add it to code'}

    print " "
