#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs 
#This module features are:


import os
import sys
from subprocess import check_call,call
import subprocess
import ast,re

import pycurl, StringIO, json
from io import BytesIO
import urllib2
import base64

class openstackRestAdaptor():
    """
    this pattern convert some interfaces of openstak classes. 
    like list images in glance and so on 
    """

    def __init__(self, params ):

        self.username = params["username"]
        self.password = params["password"]
        self.tenant = params["tenant"]
        self.controller = params["controller"]
        self.admin_token = self.get_token(self.username,self.password,self.tenant)

    def get_token(self,username,password,tenant ):


        request = json.dumps({"auth": {"tenantName": tenant  , "passwordCredentials": {"username": username  , "password": password }}})

        result = self.__curl_function(self.controller + ':5000/v2.0/tokens', \
                                      ['Content-Type: application/json', "Accept: application/json"], '200', 'POST', request)
        if not result :
            return False

        return result['access']['token']['id']


    def add_user(self,name, password,project):
        
        print "in add_users func....."

        print "list projects .........."
        #curl -i self.controller + ':5000/v3/projects' -H 'X-Auth-Token:'+ self.admin_token 
        #find project ID.......
        
        print "create user........."
        """
        curl -i self.controller + ':5000/v3/projects' -X POST -H 'Content-Type: application/json' -H "Accept: application/json" -H 'X-Auth-Token:'+ self.admin_token  -d \
            '"user": {' + \
                '"default_project_id":' +  project_id + ','+ \
                '"description": "Demo User",' + \
                '"email": '+ name + ',' \
                '"enabled": true,' + \
                '"name":' + name + ',' \
                '"password":' + password + '}}'
        """
        return True


    def remove_user(self,name):

        print "in remove_user func....."
        print "list users & find userID....... "
        """
        curl -i self.controller + ':5000/v3/users' -H 'X-Auth-Token:'+ self.admin_token 
        #get User id 
        user_id = 0 #default
        print "remove user"
        curl -i self.controller + ':5000/v3/users/' + user_id -H 'X-Auth-Token:'+ self.admin_token -X DELETE 
        """
        return True


    def add_tenant(self, name, desc, ram, vcpu, instances):

        request = json.dumps({"project": {"description": desc , "enabled": True , "name": name, "domain_id" : "default" }})
        token = self.get_token(self.username,self.password,self.tenant)
        print "token is ", token
        result = self.__curl_function(self.controller + ':5000/v3/projects', \
                                      ['X-Auth-Token: ' + token , 'Content-Type: application/json', 'Accept: application/json'], \
                                      '201', 'POST', request)
        if not result :
            return False
        print "this tenant is added: ", result #TEST


        current_tenant_id = result['project']['id']
        print "CURRENt TENAT ID IS: " , current_tenant_id #TEST

        tenants = self. __tenants_list()
        if not tenants :
            return False
        admin_tenant_id = "" 
        for tenant in tenants :
            if  tenant['name'] == "admin" :
                        admin_tenant_id = tenant['id']
        print "ADMIN TENANT ID IS: " , admin_tenant_id #TEST
        
        request = json.dumps({"quota_set": {"cores": vcpu , "instances": instances , "ram": ram }})
        result = self.__curl_function(self.controller + ':8774/v2/' + admin_tenant_id + '/os-quota-sets/' + current_tenant_id, \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant),'Content-Type: application/json', "Accept: application/json"], \
                                      '200', 'PUT', request)
        if not result :
            return False
        print "this quota is added: ", result #TEST
        
        return True


    def __tenants_list(self):

        result = self.__curl_function(self.controller + ':5000/v3/projects', \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), "Accept: application/json"], \
                              '200', 'GET')
        if not result :
            return False

        tenats = result["projects"]
        print "all of tenants: ", tenats  #TEST
        return tenats

    def remove_tenant(self, project_name):

        if project_name is None :
            print "project name cant be Null"
            return False

        tenants = self. __tenants_list()
        if not tenants :
            return False

        tenant_ids = []
        for tenant in tenants :
            if project_name in tenant['name'] :
                tenant_ids.append(tenant['id'])

        print "Remove Projects: ", tenant_ids ##TEST 
        for i in  tenant_ids :
            result = ""
            result = self.__curl_function(self.controller + ':5000/v3/projects/' + tenant_ids.pop(), \
                                          ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), "Accept: application/json"], \
                                          '204', 'DELETE')
            if not result:
                return False

        return True
    

    def __curl_function(self, url, headers_list, response_code, method, request = None):

        data = BytesIO()        
        headers = BytesIO()        
        curlObj = pycurl.Curl()

        curlObj.setopt(pycurl.URL, url )
        curlObj.setopt(pycurl.HTTPHEADER,headers_list)
        if method == 'DELETE':
            print "in DEL"
            curlObj.setopt(pycurl.CUSTOMREQUEST,'DELETE')
        elif method == 'POST':
            print "in POST"
            curlObj.setopt(pycurl.POSTFIELDS,request)
        elif method == 'GET':
            print "in GET"
            pass
        elif method == 'PUT':
            print "in PUT"
            curlObj.setopt(pycurl.CUSTOMREQUEST,'PUT')
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
    
        #status_code = curlObj.getinfo(pycurl.HTTP_CODE)
    
        #print "In CURL function ... "
        #print "header is ", headers.getvalue() , "data is ", data.getvalue()
        if headers.getvalue() is None :
            return False

        if response_code in headers.getvalue().splitlines()[0] :
            print "SUCCESSFUL CURL Command"            
            if data.getvalue() is not "":
                return json.loads(data.getvalue())
            else :
                return True
        else :
            print "Error...", json.loads(data.getvalue())["error"]["message"]
            return False
            
        
