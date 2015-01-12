#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 15-Jan-10

#jenkins Client.
#run this code to add new built image to openstack 

import yaml, sys
import pycurl, json
from io import BytesIO

#---Python Pathes---
sys.path.append('/etc/xpl/')
import xpl_settings as settings


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

    curlObj.setopt(pycurl.WRITEFUNCTION,data.write)
    curlObj.setopt(pycurl.HEADERFUNCTION,headers.write)

    try :
        curlObj.perform()
    except Exception as e:
        print e
    curlObj.close()
        
    if headers.getvalue() is None :
        return False

    if response_code in headers.getvalue().splitlines()[0] :
        if data.getvalue() is not None:            
            return data.getvalue()
        else :
            return True
    else :
        print "Error..."
        return False



def app_spec(path) :

    f=open(path, "r")
    doc=yaml.load(f)
    appliance_info_dic={}
    appliance_info_dic["name"]    = str(doc["name"])
    appliance_info_dic["version"] = str(doc["version"])
    appliance_info_dic["url"]     = str(doc["url"])
    appliance_info_dic["author"]  = str(doc["author"])
    appliance_info_dic["tags"]    = str(doc["tags"])
    appliance_info_dic["cpu"]     = str(doc["cpu"])
    appliance_info_dic["memory"]  = str(doc["memory"])
    appliance_info_dic["storage"] = str(doc["storage"])
    appliance_info_dic["category"] = str(doc["category"])
    appliance_info_dic["author_website"] = str(doc["author_website"])
    appliance_info_dic["creation_date"] = str(doc["creation_date"])
    appliance_info_dic["installed_size"] = str(doc["installed_size"])
    appliance_info_dic["installed_size"] = str(doc["installed_size"])
    appliance_info_dic["license"] = str(doc["license"])
    appliance_info_dic["component_versions"] = str(doc["component_versions"])
    appliance_info_dic["arch"] = str(doc["arch"])
    appliance_info_dic["appliance_release_id"] = str(doc["appliance_release_id"])
    
    return appliance_info_dic



def main(path_to_appspec):
    """
    Main Program
    """
    request = {"image": app_spec(path_to_appspec)}
    url = settings.xaminCloudAgentUrl  + ':' + settings.xaminCloudAgentPort  + '/images/' + request["image"]["name"]
    header_list = ['Content-Type: application/json']
    print "URL=%s RESPONSE_CODE=%s HTTP_METHOD=%s HEADER_LIST=%s" %(url,  '200', 'POST',header_list)
    print "REQUEST=%s " % request

    result = curl(url, header_list, '200', 'POST', request)
    
    print result


if __name__ == '__main__':

    try:
        currentJobName = sys.argv[1]
        if len(sys.argv) == 2 :
            appGitName = currentJobName 
        else:
            appGitName = sys.argv[2]
        pass
    except:
        print "no appliance input given"
        sys.exit(1)

    path_to_appspec = settings.jenkinsHome + currentJobName + "/workspace/" + appGitName + "/app-spec"
    main(path_to_appspec)

    #curl -X POST 127.0.0.1:8000/images/stageb -H 'Content-Type: application/json' -d '{"image": {"name": "stageb", "url": "http://release.xamin.ir/appliances/0ad48498473444f1122c8e9883333ae6.xvm2"}}'
