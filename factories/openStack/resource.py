#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module .....
import os, sys, re
from curlWrapper import curl
import keystoneWrapper


def _get_resource_id(self, resource_type, resource_name, username=None, password=None,tenant=None):
    ''' 
    returns: a dictionary of the form {"status": "error"/"success" , "message": "error-message"/"resource-id"}
    '''        
    if username == None :
        username=self.username
        password=self.password
        tenant=self.tenant


    def _resources_list(client_type, response_code, username=None, password=None,tenant=None):

        if username == None :
            username=self.username
            password=self.password
            tenant=self.tenant

	#Getting token:
    	token_res = keystoneWrapper.get_token(self, username, password, tenant)
    	if token_res['status'] == "error":
            #print "Error in getting token for user=%s, password=%s, project=%s " %(username, password, tenant)
            token_res['message'] = "Error in getting token for user="+username +", password="+password+", project="+tenant+ "\n"+ \
                                         str(token_res['message'])
            return token_res
    	token = str(token_res['message'])

        result = curl(self.controller + str(client_type), \
                              ['X-Auth-Token: '+token, "Accept: application/json",'Access-Control-Allow-Origin: *'], response_code, 'GET')
        return result

    resources = []
    
    if resource_type == "TENANT":            
        res = _resources_list(':5000/v3/projects', '200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']["projects"]

    elif resource_type == "USER":
        res = _resources_list(':5000/v3/users','200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['users']
        
    elif resource_type == "ROLE":
        res = _resources_list(':5000/v3/roles','200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['roles']

    elif resource_type == "FLAVOR":
        res = _resources_list(':8774/v2/' + _get_resource_id(self,"TENANT", 'admin') + '/flavors','200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['flavors']

    elif resource_type == "IMAGE":
            #/v2/{tenant_id}/images
        res = _resources_list(':8774/v2/' + _get_resource_id(self,"TENANT", 'admin') + '/images','200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['images']

    elif resource_type == "SERVER":
            #/v2/{tenant_id}/servers
        res = _resources_list(':8774/v2/' + _get_resource_id(self,"TENANT", tenant) + '/servers','200', username, password,tenant)
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['servers']

    elif resource_type == "NETWORK":
        res = _resources_list(':9696/v2.0/networks','200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['networks']

    elif resource_type == "Network":
        res = _resources_list(':9696/v2.0/networks','200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['networks']

    elif resource_type == "SUBNET":
        res = _resources_list(':9696/v2.0/subnets','200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['subnets']

    elif resource_type == "ROUTER":
        res = _resources_list(':9696/v2.0/routers','200')
        if res['status'] == "error":
            print "There is not any %s on Openstack!" %(resource_type)
            return res
        resources = res['message']['routers']

    else:
        print "The %s resource is not supported..." %(resource_type)
        return {"status":"error" , "message" : "Resource Type was not found"}

    resource_id = ""
    for resource in resources :
        if resource_name == resource['name'] :
            resource_id = resource['id']

    if not resource_id :
        print "There is not resource %s with name %s on open stack!"  % (resource_type,resource_name)
        return {"status":"error" , "message" : "Resource was not found"}
    
    return {"status":"success" , "message" : str(resource_id) }



