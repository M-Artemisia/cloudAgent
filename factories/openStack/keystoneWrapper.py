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
        print "request to get token: ", request
        #print "CurL:"+self.controller + ':5000/v2.0/tokens   ' + 'Content-Type: application/json    ' + 'Accept: application/json    ' + 'Access-Control-Allow-Origin: *    ' + '200'+ '   POST'
	print "\n"
        return result
    return {"status":"success", "message": str(result['message']['access']['token']['id'])}


def add_user(self,name, password,project):
    
    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if tenant_id['status'] == "error" :
 	tenant_id['message'] = "Add user: error in getting resource id:\n"+ str(tenant_id['message'])
        return tenant_id
    tenant_id = tenant_id['message']

    #Getting token:
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
        token['message'] = "Add user: Error in getting token for user="+ self.username +", password="+ self.password \
					+", project="+ self.tenant + "\n"+ str(token['message'])
        return token
    token = token['message']
  
    request = {"user": {"name": name , "password": password, "email" : name, "default_project_id": tenant_id }}
    result = curl(self.controller + ':5000/v3/users', ['X-Auth-Token: ' + str(token) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if result['status'] == "error" :
	result['message'] = "Failed to add user:\n" + str(result['message'])
        return result

    result = _add_user_role(self, name, project)
    if result['status'] == "error" :
        return result #The message is already in result :)
    print "user %s added to project %s" %(name, project)
    return result


def _add_user_role(self, username, project):
    
    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if tenant_id['status'] == "error" :
	tenant_id['message'] = "Add user role: error in getting resource id:\n"+ tenant_id['message']
        return tenant_id
    tenant_id = tenant_id['message']

    user_id = resource._get_resource_id(self,"USER",username)
    if user_id['status'] == "error" :
	user_id['message'] = "Add user role: error in getting resource id:\n" + user_id['message']
        return user_id
    user_id = user_id['message']
    
    #Getting token:
    #token = get_token(self, self.username,self.password,self.tenant)
    token = get_token(self, self.username,self.password,"ttt")
    if token['status'] == "error":
	print token['message']
    	token['message'] = "Add user role: Error in getting token for user="+ str(self.username) +", password="+ str(self.password) \
                + ", project="+ str(self.tenant) + "\n"+ str(token['message'])
        return token
    token = token['message']
   

    self.member_role_id_res= resource._get_resource_id(self,"ROLE","_member_")
    if self.member_role_id_res['status'] == "error" :
        s = "It seems the Openstack has not correct roles for _member_ \n"+ self.member_role_id_res['message']
        return {'status' :'error', 'message': s}
    member_role_id = self.member_role_id_res['message']


    result = curl(self.controller + ':5000/v3/projects/' + tenant_id + 'ttt/users/' + user_id + '/roles/' + member_role_id , \
                      ['X-Auth-Token: ' + str(token) , 'Content-Type: application/json','Access-Control-Allow-Origin: *'], '204', 'PUT')

    if result['status'] == "error" :
	# jabbari: str(result['message']) failed because result['message'] was unicode string
	result['message'] = "Failed to add role:\n" + result['message']
        return result
    return result

def remove_user(self,username):

    user_id = resource._get_resource_id(self,"USER",username)
    if user_id['status'] == "error" :
	user_id['message'] = "Remove user: error in getting resource id:\n"+ str(user_id['message'])
        return user_id
    user_id = user_id['message']

    #Getting token:
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
	token_res['message'] = "Remove user: Error in getting token for user="+ self.username +", password="+ self.password+ \
                ", project="+ self.tenant + "\n"+ str(token_res['message'])
        return token
    token = token['message']

    result = curl(self.controller + ':5000/v3/users/' + user_id, ['X-Auth-Token: ' + str(token)], '204', 'DELETE')
    #if result['status'] == "error":
    #    return result
    return result


def add_tenant(self, name, desc, ram, vcpu, instances):

    #*******ADDING TENANT******
    request = {"project": {"description": desc , "enabled": True , "name": name, "domain_id" : "default" }}
        
    #Getting token:
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
    	token['message'] = "Add tenant: Error in getting token for user="+ self.username +", password="+ self.password \
                +", project="+ self.tenant + "\n"+ str(token['message'])
        return token
    token = token['message']

    result = curl(self.controller + ':5000/v3/projects', ['X-Auth-Token: ' + str(token) ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if result['status'] == "error" :
	result['message'] = "Add tenant: Failed to add project: \n"+ str(result['message'])
        return result
    result = result['message']

    #*******ADDING QUOTA******
    current_tenant_id = result['project']['id'];
    admin_tenant_id = resource._get_resource_id(self,"TENANT","admin")
    if admin_tenant_id['status'] == "error":
	admin_tenant_id['message'] = "Add tenant - add quota: Cannot find tenant id for admin :\n"+ str(admin_tenant_id['message'])
	return admin_tenant_id
    admin_tenant_id = admin_tenant_id['message']

    #getting token - using the one taken before :)

    request = {"quota_set": {"cores": vcpu , "instances": instances , "ram": ram }}
    result = curl(self.controller + ':8774/v2/' + str(admin_tenant_id) + '/os-quota-sets/' + str(current_tenant_id), \
        ['X-Auth-Token: ' + str(token),'Content-Type: application/json', "Accept: application/json" \
						,'Access-Control-Allow-Origin: *'], '200', 'PUT', request)
    if result['status'] == "error" :
	result['message'] = "Add tenant: Failed to add quota: \n"+ str(result['message'])
        return result
    return result


def remove_tenant(self, project_name):

    if project_name is None :
        print "Failed to remove tenant: project name cant be Null"
        return {'status':'error', 'message':'Remove tenant: Project name cannot be null'}

    tenant_id = resource._get_resource_id(self,"TENANT",project_name)
    if tenant_id['status'] == "error":
        tenant_id['message'] = "Remove tenant: error in getting resource id:\n"+ str(tenant_id['message'])
        return tenant_id
    tenant_id = str(tenant_id['message'])

    # Getting token
    token = get_token(self, self.username,self.password,self.tenant)
    if token['status'] == "error":
	token_res['message'] = "Remove tenant: Error in getting token for user="+ self.username +", password="+ self.password+ \
                ", project="+ self.tenant + "\n"+ str(token_res['message'])
        return token
    token = token['message']

    result = ""
    result = curl(self.controller + ':5000/v3/projects/' + str(tenant_id), \
                      ['X-Auth-Token: ' + token , "Accept: application/json",'Access-Control-Allow-Origin: *'], '204', 'DELETE')
    if result['status'] == "error":
        result['message'] = "Add tenant: Failed to add quota: \n"+ str(result['message'])
        return result
    return result



""" 
    self.admin_role_id_res= resource._get_resource_id(self,"TENANT",'admin')
    if self.member_role_id_res['status'] == "error":
        s = "It seems the Openstack has not correct roles for admin \n"+str(self.admin_token_res['message'])
        return {'status' :'error', 'message': s}
    self.admin_role_id = self.admin_role_id_res['message']

"""
