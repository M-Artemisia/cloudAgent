#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re, time
from curlWrapper import curl
import resource
import keystoneWrapper, neutronWrapper
from time import sleep

def install_server(self, user, password, project, instance_name, external_ip_pool, internal_ip_pool,server_user, server_pass, security_group = 'default', image='cirros-2', flavor='m1.small'):
    '''
    Assumptions: the xaas_for_startup for flavor & external network is assigned by default
    TODO: i use int as internal_network_NAME. we shpuld find the name of the internal net based on router:external element of the network API
    '''

    #print "flavor in install_server is: ", flavor    
    print "Install server..."
    print "STEP 1"

    internal_net_id = resource._get_resource_id(self,"NETWORK",internal_ip_pool)
    if internal_net_id['status'] == "error":
	internal_net_id['message'] = "Install Server Step 1: error in getting resource id:\n"+ str(internal_net_id['message'])
	return internal_net_id
    internal_net_id =  str(internal_net_id['message'])

    image_id = resource._get_resource_id(self,"IMAGE",image)
    if image_id['status'] == "error":
        image_id['message'] = "Install Server Step 1: error in getting resource id:\n"+ str(image_id['message'])
	return image_id
    image_id = image_id['message']

    flavor_id = resource._get_resource_id(self,"FLAVOR",flavor)
    if flavor_id['status'] == "error":
        flavor_id['message'] = "Install Server Step 1: error in getting resource id:\n"+ str(flavor_id['message'])
	return flavor_id
    flavor_id = flavor_id['message']

    print "STEP 2"
    request = {"server":{ \
            "name": instance_name,\
                "imageRef": image_id,\
                "flavorRef": flavor_id,\
                "networks": [{"uuid": internal_net_id }],\
                "security_groups": [{"name": security_group}]}}

    print "STEP 3"
    tenant_id_res = resource._get_resource_id(self,"TENANT",project)
    if tenant_id_res['status'] == "error" :
    	tenant_id_res['message'] = "Install Server Step 3: error in getting resource id:\n"+ str(tenant_id_res['message'])
        return tenant_id_res
    tenant_id = str(tenant_id_res['message'])

    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Install Server Step 3: error in getting resource id:\n"+ str(token_res['message'])
        return token_res
    token = token_res['message']

    result = curl(self.controller + ':8774/v2/' + tenant_id + '/servers', \
                      ['X-Auth-Token: ' + token ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '202', 'POST', request)
    print "STEP 4"
    if result['status'] == "error" :
        print "Failed to install server"
	result['message'] = "Install Server Step 4: Failed to install server :\n"+ str(result['message'])
        return result

    print "STEP 5"
    #sleep(10)
    network_res = neutronWrapper._assign_float_ip(self, user, password, project, external_ip_pool, instance_name)
    if network_res['status'] == "error":
        network_res['message'] = "Install Server Step 5: Failed to assign float ip :\n"+ str(network_res['message'])
        return network_res
    network = network_res['message']

    print "STEP 6"

    octets = re.split('(.*)\.(.*)\.(.*)\.(.*)', network)
    print "the image is installed. its invalid_ip: %s and the valid_ip: 217.218.62.%s" %(network, str(octets[4:5].pop()))

    print "STEP 7"

    return {'status':'success','message': "217.218.62."+str(octets[4:5].pop())}


def remove_server(self, user, password, project, server):

    tenant_id_res = resource._get_resource_id(self,"TENANT",project)
    if tenant_id_res['status'] == "error" :
    	tenant_id_res['message'] = "Remove Server Step 1: error in getting resource id:\n"+ str(tenant_id_res['message'])
        return tenant_id_res
    tenant_id = str(tenant_id_res['message'])

    print "Remove Server STEP 1: tenant_id is ",tenant_id 

    ##server_id = resource._get_resource_id(self,"SERVER",server, self.username, self.password, self.tenant)
    #server_id = resource._get_resource_id(self,"SERVER",server, user, password, project)
    ##server_id = resource._get_resource_id(self,"SERVER",server,project)
    server_id_res = resource._get_resource_id(self,"SERVER",server, user, password, project)
    if server_id_res['status'] == "error" :
	server_id_res['message'] = "Remove Server Step 1: error in getting resource id:\n"+ str(server_id_res['message'])
	return server_id_res
    server_id = str(server_id_res['message'])
    print "Server id is : ", server_id

    #----- Add to get float_ip associated with the server to release
    #The code works when there is only one floating_ip in the tenant. 
    #In demo, the server and the ip associated to it, are created in their tenant. so it's ok to just retrun the first entry of the curl result :)
    print "Remove Server STEP 2: release float ip"
    #1_"getting the float ip id"
    #float_ip_id = resource._get_floatip_id(self,"FLOATIP", tenant_id, user, password, project)
    
    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Remove server Step 2: release floating ip: Error in getting token for user=" \
				 +user+ ", password=" + password +" , project=" + project+ ":\n"+ str(token_res['message'])
	return token_res
    token = token_res['message']
    #

    float_ip_id = ""
    float_ip = ""
    result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips', ['X-Auth-Token: ' + token ,\
                               'Accept: application/json', 'Access-Control-Allow-Origin: *'], '200', 'GET')
    if result['status'] == "error" :
	print "No floating ip found for the tenant_id" #only print, no error return value
    else:
    	print "floating_ips for the tenant : ", result
	result = result['message']
        try:
	    float_ip_id = result['floating_ips'][0]['id']
	    float_ip = result['floating_ips'][0]['ip']
	    print float_ip
	    print "id: ", float_ip_id
	except:
	    print "Something is wrong with float ip - the id could not be found" #only print, no error return value
    

    if float_ip_id and not float_ip_id.isspace():  #if float_ip_id != "":
        try:
	    ''' # ----We may need to add this part... 
 	    #"2_removing the float ip from the server"
    	    request = {"removeFloatingIp": {"address": str(float_ip)}}
    	    result = curl(self.controller + ':8774/v2/' + tenant_id + '/servers/' + str(server_id) +'/action', \
            	['X-Auth-Token: ' + token ,'Content-Type: application/json', \
			'Accept: application/json', 'Access-Control-Allow-Origin: *'], '202', 'POST',request)
	    #deallocate_float_ip(self, user, password, project, tenant_id, id)
    	    if result['status'] == "error" :
        	print "Cannot disassociate floating ip from the server" #only print, no error return value
    	    else:
        	print "Floating ip disassociated from the server" #only print, no error return value
   	    '''

	    #3_deallocating float ip - DO NOT USE ADMIN TOKEN! You can only deallocate ips allocated to a tenant using the token for that tenant!!
            """ipresult = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips/' + str(float_ip_id) , ['X-Auth-Token: ' + token ,\
                                'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      	'202', 'DELETE')"""
	    ipresult = deallocate_float_ip(self, user, password, project, tenant_id, str(float_ip_id))
	    if ipresult['status'] == "error" :
                print "STEP 2: Cannot deallocate floating IP from the server!!--" #only print, no error return value
                #return False #We don't retrun Flase here
            else :
                print "Remove Server STEP 2: Floating ip deallocated" #only print, no error return value
        except:
            print "Remove Server STEP 2: Cannot deallocate floating IP from the server!!--"  #only print # We Don't return false
     	    

    print "Remove Server STEP 3: server_id is ", server_id

    request = '{"force_delete": null}'
    
    result = curl(self.controller + ':8774/v2/'+ tenant_id + '/servers/' + server_id, \
		['X-Auth-Token: ' + token ,'Content-Type: application/json', 'Accept: application/json',\
 				'Access-Control-Allow-Origin: *'], '204', 'DELETE')
    
    #print self.controller + ':8774/v2/'+ tenant_id + '/servers/' + server_id +'HEADERS: X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username, self.password, self.tenant) + '  -H Content-Type: application/json'+'  -H Accept: application/json   '+'  -H Access-Control-Allow-Origin: *'+'  204', '  DELETE'
    print "STEP 4: "
    if result['status'] == "error" :
  	print "Failed to remove server : "
	result['message'] = "Remove Server Step 4: Failed to remove server : \n"+ str(result['message']) 
	return result
    print "server is removed"
    return result  #result is not used, only success is important


def add_flavor(self, user, password, project, flavor_name, ram, vcpus, disk):
    #ram based on M, disk Based on G
    print "Flavor Add Function "
    
    tenant_id_res = resource._get_resource_id(self,"TENANT",self.tenant) #self.tenant, not project!
    if tenant_id_res['status'] == "error" :
	tenant_id_res['message'] = "Add Flavor: error in getting resource id:\n"+ tenant_id_res['message']
        return tenant_id_res
    tenant_id = str(tenant_id_res['message'])


    #Getting token:
    #token_res = keystoneWrapper.get_token(self, user, password, project)
    token_res = keystoneWrapper.get_token(self, self.username,self.password,self.tenant)
    if token_res['status'] == "error":
	token_res['message'] = "Add flavor: Error in getting token for user=" +self.username+ \
				", password=" + self.password +" , project=" + self.tenant +" \n"+ str(token_res['message'])
        return token_res
    token = token_res['message']
    #

    request = {"flavor": {"name": flavor_name, "ram": ram, "vcpus" : vcpus, "disk" : disk ,"id": time.strftime("%Y%m%d_%H%M%S", time.gmtime()) }}
    result = curl(self.controller + ':8774/v2/'+ tenant_id + '/flavors', \
    		['X-Auth-Token: ' + token , 'Content-Type: application/json', \
			'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'POST', request)
    if result['status'] == "error":
	print "Cannot add flavor"
	result['message'] = "Cannot add flavor: \n" + str(result['message'])
        return result
    print "flavor is added"
    return result


def remove_flavor(self, user, password, project,flavor):

    print "Testing Flavor Remove Function "
    tenant_id_res = resource._get_resource_id(self,"TENANT", self.tenant) #self.tenant, not project
    if tenant_id_res['status'] == "error" :
        tenant_id_res['message'] = "Remove Flavor: error in getting resource id:\n" + str(tenant_id_res['message'])
        return tenant_id_res
    tenant_id = str(tenant_id_res['message'])

    flavor_id = resource._get_resource_id(self,"FLAVOR",flavor)
    if flavor_id['status'] == "error" :
        flavor_id['message'] = "Remove Flavor: error in getting resource id:\n" + str(flavor_id['message'])
        return flavor_id
    flavor_id = flavor_id['message']

    #Getting token:
    #token_res = keystoneWrapper.get_token(self, user, password, project)
    token_res = keystoneWrapper.get_token(self, self.username,self.password,self.tenant)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
	token_res['message'] = "Remove flavor: Error in getting token for user=" +self.username+ \
                                ", password=" + self.password +" , project=" + self.tenant +" \n"+ str(token_res['message'])
        return token_res
    token = token_res['message']
    #

    result = curl(self.controller + ':8774/v2/'+ tenant_id + '/flavors/' + flavor_id, \
                      ['X-Auth-Token: ' + token ,'Content-Type: application/json', 'Accept: application/json', \
 				'Access-Control-Allow-Origin: *'], '202', 'DELETE')
    if result['status'] == "error" :
	print "Cannot remove flavor"
        result['message'] = "Cannot remove flavor: \n" + str(result['message'])
        return result
    print "flavor is removed"
    return result


def deallocate_float_ip(self, user, password, project, tenant_id, id):
    ''' 
    Added by jabbari -only ips for that project could be deallocated
    '''
    #print "id is ", id
    #print "tenant id is ", tenant_id

    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        token_res['message'] = "Deallocate_float_ip: Error in getting token for user=" + user+ \
                                ", password=" + password +" , project=" + project +" \n"+ str(token_res['message'])
        return token_res
    token = token_res['message']
    #

    result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips/' + str(id)  , \
                ['X-Auth-Token: ' + token ,'Content-Type: application/json', \
			'Accept: application/json', 'Access-Control-Allow-Origin: *'],'202', 'DELETE')
    if result['status'] == "error" :
        result['message'] = "--IP deallocate Failed--: "+ str(result['message'])
        return result
    result['message'] = "--IP deallocated--: "+ str(result['message'])
    return result

#added by jabbari
def list_float_ips(self, user, password, project, tenant_id):

    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
    	token_res['message'] = "List_float_ips: Error in getting token for user=" + user \
                                + ", password=" + password +" , project=" + project +" \n"+ str(token_res['message'])
        return token_res
    token = token_res['message']
    #    

    result = curl('10.1.48.242:8774/v2/' + tenant_id + '/os-floating-ips', \
                      ['X-Auth-Token: '  + token , 'Content-Type: application/json', \
				'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'GET')
    if result['status'] == "error" :
        result['message'] = "Failed to get list of floating ips for tenant "+ str(tenant_id) +":\n"+ str(result['message'])
        return result

    return result

