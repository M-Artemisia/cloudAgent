#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module .....
import os, sys, re
from curlWrapper import curl
import keystoneWrapper

def _get_resource_id(self, resource_type, resource_name):
        
    def _resources_list(client_type, response_code):
        result = curl(self.controller + str(client_type), \
                              ['X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username,self.password,self.tenant), "Accept: application/json",'Access-Control-Allow-Origin: *'], response_code, 'GET')
        if not result :
            return False
        return result

    resources = []
    if resource_type == "TENANT":            
        res = _resources_list(':5000/v3/projects', '200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res["projects"]

    elif resource_type == "USER":
        res = _resources_list(':5000/v3/users','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['users']
        
    elif resource_type == "ROLE":
        res = _resources_list(':5000/v3/roles','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['roles']

    elif resource_type == "FLAVOR":
            #/v2/{tenant_id}/flavors
        res = _resources_list(':8774/v2/' + _get_resource_id(self,"TENANT", 'admin') + '/flavors','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['flavors']

    elif resource_type == "IMAGE":
            #/v2/{tenant_id}/images
        res = _resources_list(':8774/v2/' + _get_resource_id(self,"TENANT", 'admin') + '/images','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['images']
    elif resource_type == "SERVER":
            #/v2/{tenant_id}/servers
        res = _resources_list(':8774/v2/' + _get_resource_id(self,"TENANT", 'DemoTest') + '/servers','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['servers']

    elif resource_type == "NETWORK":
        res = _resources_list(':9696/v2.0/networks','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['networks']

    elif resource_type == "Network":
        res = _resources_list(':9696/v2.0/networks','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['networks']

    elif resource_type == "SUBNET":
        res = _resources_list(':9696/v2.0/subnets','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['subnets']

    elif resource_type == "ROUTER":
        res = _resources_list(':9696/v2.0/routers','200')
        if not res:
            print "There is not any %s on Openstack!" %(resource_type)
            return False
        resources = res['routers']

    else:
        print "The %s resource is not supported..." %(resource_type)
        return False 

    resource_id = ""
    for resource in resources :
        if resource_name == resource['name'] :
            resource_id = resource['id']

    if not resource_id :
        print "There is not resource %s with name %s on open stack!"  % (resource_type,resource_name)
        return False
    
    return str(resource_id)



