#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os
import sys
import pycurl, json
from io import BytesIO

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
        
        tenants = self. __tenants_list()
        if not tenants :
            return False
        tenant_id = "" 
        for tenant in tenants :
            if tenant['name'] == project :
                tenant_id = tenant['id']

        request = json.dumps({"user": {"name": name , "password": password, "email" : name, "default_project_id": tenant_id }})
        result = self.__curl_function(self.controller + ':5000/v3/users', \
                                      ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant) ,\
                                       'Content-Type: application/json', 'Accept: application/json'], \
                                      '201', 'POST', request)
        if not result :
            return False
        print "the added user is: "; print result; print; print #TEST
        return True


    def remove_user(self,username):

        users = self.list_users()
        if not users :
            return False
        user_id = ""
        for user in users :
            if username == user['name'] :
                user_id = user['id']
        if user_id == "":
            print "There is not such user in open stack users!"
            return False
        print "Remove User: name = %s id = %s " % (username, user_id) ; print; print ##TEST 
        result = self.__curl_function(self.controller + ':5000/v3/users/' + user_id, \
                                          ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant)], \
                                          '204', 'DELETE')
        if not result:
            return False

        return True


    def list_users(self):

        result = self.__curl_function(self.controller + ':5000/v3/users', \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant)], \
                              '200', 'GET')
        if not result :
            return False
        users = result["users"]
        #print "all of Users: ", users  #TEST
        return users


    def add_tenant(self, name, desc, ram, vcpu, instances):

        request = json.dumps({"project": {"description": desc , "enabled": True , "name": name, "domain_id" : "default" }})
        result = self.__curl_function(self.controller + ':5000/v3/projects', \
                                      ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant) ,\
                                       'Content-Type: application/json', 'Accept: application/json'], \
                                      '201', 'POST', request)
        if not result :
            return False
        print "this tenant is added: "; print result; print; print #TEST

        current_tenant_id = result['project']['id']
        print "CURRENt TENAT ID IS: " , current_tenant_id #TEST

        tenants = self. __tenants_list()
        if not tenants :
            return False
        admin_tenant_id = "" 
        for tenant in tenants :
            if  tenant['name'] == "admin" :
                        admin_tenant_id = tenant['id']
        print "ADMIN TENANT ID IS: " , admin_tenant_id;  print; print#TEST
        
        request = json.dumps({"quota_set": {"cores": vcpu , "instances": instances , "ram": ram }})
        result = self.__curl_function(self.controller + ':8774/v2/' + admin_tenant_id + '/os-quota-sets/' + current_tenant_id, \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant),'Content-Type: application/json', "Accept: application/json"], \
                                      '200', 'PUT', request)
        if not result :
            return False
        print "this quota is added: ";print result; print; print #TyEST
        
        return True


    def __tenants_list(self):

        result = self.__curl_function(self.controller + ':5000/v3/projects', \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), "Accept: application/json"], \
                              '200', 'GET')
        if not result :
            return False

        tenats = result["projects"]
        #print "all of tenants: ", tenats  #TEST
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
        if not tenant_ids :
            print "There is not such project on open stack!"
            return False
        print "Remove Projects: name = %s id = %s" % (project_name, tenant_ids) ##TEST 
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
            curlObj.setopt(pycurl.CUSTOMREQUEST,'DELETE')
        elif method == 'POST':
            curlObj.setopt(pycurl.POSTFIELDS,request)
        elif method == 'GET':
            pass
        elif method == 'PUT':
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
        if headers.getvalue() is None :
            return False

        if response_code in headers.getvalue().splitlines()[0] :
            if data.getvalue() is not "":
                return json.loads(data.getvalue())
            else :
                return True
        else :
            print "Error...", json.loads(data.getvalue())["error"]["message"]
            return False
            
        
