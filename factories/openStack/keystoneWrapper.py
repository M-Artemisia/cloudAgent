#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re
from curlWrapper import curl
import resource



def get_token(self,username,password,tenant  ):

    request = {"auth": {"tenantName": tenant  , "passwordCredentials": {"username": username  , "password": password }}}
    result = curl(self.controller + ':5000/v2.0/tokens', ['Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], '200', 'POST', request)

    return str(result['access']['token']['id'])


def add_user(self,name, password,project):
    
    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if not tenant_id :
        return False
    request = {"user": {"name": name , "password": password, "email" : name, "default_project_id": tenant_id }}
    result = curl(self.controller + ':5000/v3/users', \
                      ['X-Auth-Token: ' + get_token(self, self.username,self.password,self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if not result :
        return False

    result = _add_user_role(self, name, project)
    if not result :
        return False

    return result 


def _add_user_role(self, username, project):
    
    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if not tenant_id :
        return False

    user_id = resource._get_resource_id(self,"USER",username)
    if not user_id :
        return False

    result = curl(self.controller + ':5000/v3/projects/' + str(tenant_id) + '/users/' + str(user_id) + '/roles/' + str(self.member_role_id) , \
                      ['X-Auth-Token: ' + get_token(self, self.username,self.password,self.tenant), 'Content-Type: application/json','Access-Control-Allow-Origin: *'], '204', 'PUT')

    if not result :
        return False
    return result 

def remove_user(self,username):

    user_id = resource._get_resource_id(self,"USER",username)
    if not user_id:
        return False

    result = curl(self.controller + ':5000/v3/users/' + user_id, \
                      ['X-Auth-Token: ' + get_token(self, self.username,self.password,self.tenant)], \
                      '204', 'DELETE')
    if not result:
        return False
    return result


def add_tenant(self, name, desc, ram, vcpu, instances):

        #*******ADDING TENANT******
    request = {"project": {"description": desc , "enabled": True , "name": name, "domain_id" : "default" }}
    result = curl(self.controller + ':5000/v3/projects', \
                      ['X-Auth-Token: ' + get_token(self, self.username,self.password,self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if not result :
        return False

        #*******ADDING QUOTA******
    current_tenant_id = result['project']['id'];
    admin_tenant_id = resource._get_resource_id(self,"TENANT","admin");
    
    request = {"quota_set": {"cores": vcpu , "instances": instances , "ram": ram }}
    result = curl(self.controller + ':8774/v2/' + str(admin_tenant_id) + '/os-quota-sets/' + str(current_tenant_id), \
                      ['X-Auth-Token: ' + get_token(self, self.username,self.password,self.tenant),'Content-Type: application/json', "Accept: application/json",'Access-Control-Allow-Origin: *'], '200', 'PUT', request)
    if not result :
        return False        
    return True


def remove_tenant(self, project_name):

    if project_name is None :
        print "project name cant be Null"
        return False

    tenant_id = resource._get_resource_id(self,"TENANT",project_name)
    if not tenant_id:
        return False

    result = ""
    result = curl(self.controller + ':5000/v3/projects/' + str(tenant_id), \
                      ['X-Auth-Token: ' + get_token(self, self.username,self.password,self.tenant), "Accept: application/json",'Access-Control-Allow-Origin: *'], '204', 'DELETE')
    if not result:
        return False
    return result
