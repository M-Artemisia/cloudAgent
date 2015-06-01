#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re
from curlWrapper import curl
import resource


def get_token(self,username,password,tenant):
    ''' 
    return: returns a dictionary of the form: {"status":"error"/"success" , "message": "error-message"/"token"}
    '''

    request = {"auth": {"tenantName": tenant , "passwordCredentials": {"username": username , "password": password }}}
    result = curl(self.controller + ':5000/v2.0/tokens', ['Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], '200', 'POST', request)
    if result['status'] == "error" :
        print "KEYSTONE:   ************************************************************************************"
        print "request: ", request
        print "CurL:"+self.controller + ':5000/v2.0/tokens   ' + 'Content-Type: application/json    ' + 'Accept: application/json    ' + 'Access-Control-Allow-Origin: *    ' + '200'+ '   POST'
        return result
    return {"status":"success" , "message": str(result['message']['access']['token']['id'])}


def add_user(self,name, password,project):
    
    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if tenant_id['status'] == "error" :
        return tenant_id
    tenant_id = tenant_id['message']

    #Getting token:
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
        print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        #token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
        #                                 str(token_res['message'])
        return token
    token = str(token['message'])
    
    request = {"user": {"name": name , "password": password, "email" : name, "default_project_id": tenant_id }}
    result = curl(self.controller + ':5000/v3/users', ['X-Auth-Token: ' + token ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if result['status'] == "error" :
        return result

    result = _add_user_role(self, name, project)
    if result['status'] == "error" :
        return result
    print "user %s added to project %" %(name, project)
    return result


def _add_user_role(self, username, project):
    
    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if tenant_id['status'] == "error" :
        return tenant_id
    tenant_id = tenant_id['message']

    user_id = resource._get_resource_id(self,"USER",username)
    if user_id['status'] == "error" :
        return user_id
    user_id = user_id['message']

    #Getting token:
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
        print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        return token
    token = str(token['message'])

    result = curl(self.controller + ':5000/v3/projects/' + str(tenant_id) + '/users/' + str(user_id) + '/roles/' + str(self.member_role_id) , \
                      ['X-Auth-Token: ' + token, 'Content-Type: application/json','Access-Control-Allow-Origin: *'], '204', 'PUT')

    #if result['status'] == "error" :
    #    return result
    return result

def remove_user(self,username):

    user_id = resource._get_resource_id(self,"USER",username)
    if user_id['status'] == "error" :
        return user_id
    user_id = user_id['message']

    #Getting token:
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
        print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        return token
    token = str(token['message'])

    result = curl(self.controller + ':5000/v3/users/' + user_id, ['X-Auth-Token: ' + token], '204', 'DELETE')
    #if result['status'] == "error":
    #    return result
    return result


def add_tenant(self, name, desc, ram, vcpu, instances):

    #*******ADDING TENANT******
    request = {"project": {"description": desc , "enabled": True , "name": name, "domain_id" : "default" }}
        
    #Getting token:
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
        print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        return token
    token = str(token['message'])

    result = curl(self.controller + ':5000/v3/projects', ['X-Auth-Token: ' + token ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if result['status'] == "error" :
        return result
    result = result['message']
    #*******ADDING QUOTA******
    current_tenant_id = result['project']['id'];
    admin_tenant_id = resource._get_resource_id(self,"TENANT","admin");
    if admin_tenant_id['status'] == "error":
	admin_tenant_id['message'] = "Cannot find tenant id for admin : "+ str(admin_tenant_id['message'])    
	return admin_tenant_id
    admin_tenant_id = admin_tenant_id['message']

    # Getting token
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
	return token
    token = token['message']

    request = {"quota_set": {"cores": vcpu , "instances": instances , "ram": ram }}
    result = curl(self.controller + ':8774/v2/' + str(admin_tenant_id) + '/os-quota-sets/' + str(current_tenant_id), \
        ['X-Auth-Token: ' + token,'Content-Type: application/json', "Accept: application/json",'Access-Control-Allow-Origin: *'], '200', 'PUT', request)
    #if result['status'] == "error" :
    #    return result
    return result


def remove_tenant(self, project_name):

    if project_name is None :
        print "project name cant be Null"
        return {'status':'error', 'message':'Project name cannot be null'}

    tenant_id = resource._get_resource_id(self,"TENANT",project_name)
    if tenant_id['status'] == "error":
        return tenant_id
    tenant_id = tenant_id['message']

    # Getting token
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
        return token
    token = token['message']

    result = ""
    result = curl(self.controller + ':5000/v3/projects/' + str(tenant_id), \
                      ['X-Auth-Token: ' + token , "Accept: application/json",'Access-Control-Allow-Origin: *'], '204', 'DELETE')
    #if result['status'] == "error":
    #    return result
    return result
