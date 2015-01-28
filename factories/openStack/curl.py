#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 15-Jan-10

#This module provide a fascade fauction on pycurl.
#you just need to pass some parameters to the function, and it does it all!



import os
import sys
import pycurl, json
from io import BytesIO

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
    @return: if every thing be ok, and the reponse had a body, it returns the body of the message, if it had not body, it returns True, and if an error occured it will print the Error message and return False
    """

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
        print "Unkonw http method....", method
        return False

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
        print e
    curlObj.close()
        
    #status_code = curlObj.getinfo(pycurl.HTTP_CODE)    
    if headers.getvalue() is None :
        return False

    if response_code in headers.getvalue().splitlines()[0] :
        if data.getvalue() is not None:
            return json.loads(data.getvalue())
        else :
            return True
    else :
        print "Error...", json.loads(data.getvalue())["error"]["message"]
        return False
