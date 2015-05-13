#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re
from curlWrapper import curl
from time import sleep

import resource
import keystoneWrapper, computeWrapper

#Jabbari: The code Checks to see if there is any free allocated ip for the tenant. if yes returns it and if no, allocates a new one.
def _generate_new_float_ip(self, user, password, project, tenant_id, pool):

    request = {"pool": pool}
    float_ip_id = ""
    associated = False
    
    try:
    	result = computeWrapper.list_float_ips(self, user, password, project, tenant_id)  #you cannot list ips when token does not match the project.
    	#print "--list of floating ips for tenenat ",tenant_id
    	print result

       	print "Trying to find free floating ips and associate one to the server"
	
    	for i in range(0, len(result['floating_ips'])):
	    if associated:
		break
            if not result['floating_ips'][i]['fixed_ip']:
            	id = result['floating_ips'][i]['id']
		ip = result['floating_ips'][i]['ip']
		print "fixed ip none for id ", id
            	# first we should see the details (to ensure it's status id DOWN)
            	#res = get_floating_ip_detail(tenant_id, id, token)
            	#print str(res) 
            	#Returns No more info that what we had before :(

            	# We can associate the ip to the server
                print "We are going to associate the ip ", ip
    		return ip


	#if not associated, allocate a new IP:
	result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'POST', request)
    	if not result :
            return False

    	return result['floating_ip']['ip']

    except:
	print "An exception occured in generating or associating float ip"
	return False

"""def _generate_new_float_ip(self, user, password, project, tenant_id, pool):

    
    request = {"pool": pool}
    result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'POST', request)
    if not result :
        return False
        
    return result['floating_ip']['ip']
"""

def _assign_float_ip(self, user, password, project, external_ip_pool, server):

    import resource 
    print 
    print resource
    print type(resource)
    print


    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if not tenant_id :
        print "cant find the project ",tenant_id 
        return False

    float_ip = _generate_new_float_ip(self, user, password, project, tenant_id, external_ip_pool) 
    if not float_ip:
        False
 
    request = {"addFloatingIp": {"address": float_ip}} 
    #/v2/{tenant_id}/servers
    sleep(5)
    res = curl(self.controller + str(':8774/v2/' + tenant_id + '/servers'), \
                   ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project), "Accept: application/json",'Access-Control-Allow-Origin: *'], '200', 'GET')
           
    if not res:
        print "cant find server list!"
        return False
    resources = res['servers']

    server_id = ""
    for resource in resources :
        if server in resource['name'] :
            server_id = resource['id']

    if not server_id :
        print "There is not server  with name %s on open stack!"  % (server)
        return False
    #print "The ID of the  server, with name %s is  %s" % (str(server), str(server_id))


    result = curl(self.controller + str(':8774/v2/' + tenant_id + '/servers/' + server_id +'/action'), \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'202', 'POST', request)
    #  -H "X-Auth-Project-Id: demo" -H "User-Agent: python-novaclient"
    if not result :
        print "Neutron ERROR.................."
        return False
    return float_ip 

def add_network(self, user, password, project, external=False,network_name='xaas_int2'):
    """
    Create a network & a subnet for a specific project 
    """
    tenant_id = resource._get_resource_id(self,"TENANT", project);
    if not tenant_id :
        return False
    #create_network
    request = {"network":{ \
            "tenant_id": tenant_id,\
                "name": network_name,\
                "admin_state_up": "true"}}
    network = curl(self.controller + ':9696/v2.0/networks', \
                       ['X-Auth-Token: ' + keystoneWrapper.get_token( self, user, password, project ) ,\
                            'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                       '201', 'POST', request)
    if not network :
        return False

    return network

def add_subnet(self, user, password, project, network_id ,subent_name='xaas_subnet',network_address='192.168.10.0/24'):

    print "Creating SubNet..."
    request = {"subnet":{ \
            "name":subent_name,\
                "network_id": network_id ,\
                "ip_version":4,\
                "cidr": network_address}}
    subnet = curl(self.controller + ':9696/v2.0/subnets', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token( self, user, password, project ) ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if not subnet :
        return False

    return subnet

def add_router(self, user, password, project, router_name, gateway='ext-net', internal_subnet='xaas_subnet'):
    """
    Create a new router for a specific project and introduce extenal_net as a gateway to it
    Also it adds internal_network as a interface to that.
    """

    #GET IP OF EXTERNAL NETWORK
    gateway_id = resource._get_resource_id(self,"NETWORK", gateway);
    subnet_id = resource._get_resource_id(self,"SUBNET", internal_subnet)
    if not gateway_id or not subnet_id :
        print "cant find gateway=%s or subnet=%s" %(gateway_id,subnet_id)
        return False

    print "Creating Router...gateway=%s subnet=%s" %(gateway_id, subnet_id)
    #CREATE Router
    request = {"router":{ \
            "name": router_name,\
                "external_gateway_info": {"network_id":gateway_id},\
                "admin_state_up":"true"}}
    router = curl(self.controller + ':9696/v2.0/routers', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password,project ) ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if not router :
        return False
            
    #ADD Interface
    _add_interface_to_router(self,user, password, project, router_name,internal_subnet)
    return True

def _add_interface_to_router(self, user, password, project, router_name, internal_subnet ):
    print "Adding inetrface... "
    router_id = resource._get_resource_id(self,"ROUTER", router_name);
    subnet_id = resource._get_resource_id(self,"SUBNET", internal_subnet)
    request = {"subnet_id": subnet_id }
    interface = curl(self.controller + ':9696/v2.0/routers/'+ router_id + "/add_router_interface", \
                         ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project ) ,\
                              'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                         '200', 'PUT', request)
    if not interface :
        return False
    
    return True




def remove_network(self, user, password, project, network):

    net_id = resource._get_resource_id(self,"NETWORK",network)
    if not net_id :
        return False

    result = curl(self.controller + ':9696/v2.0/networks/'+ net_id, \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username,self.password,self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '204', 'DELETE')
    if not result :
        return False

    print "Network is removed"
    return result


def remove_subnet(self, user, password, project, subnet):

    subnet_id = resource._get_resource_id(self,"SUBNET",subnet)
    if not subnet_id :
        return False

    print "user pass and subnet in this project is: "
    result = curl(self.controller + ':9696/v2.0/subnets/'+ subnet_id, \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username,self.password,self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '204', 'DELETE')
    if not result :
        return False
    print "subNetwork is removed"
    return result



def remove_router(self, user, password, project, router):
    print "Testing Remove Router Function "

    router_id = resource._get_resource_id(self,"ROUTER",router)
    if not router_id :
        return False

    result = curl(self.controller + ':9696/v2.0/routers/'+ router_id, \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username,self.password,self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '204', 'DELETE')
    if not result :
        return False
    print "Router is removed"
    return result


def remove_interface_from_router(self, user, password, project, router, subnet ):
    print "Testing Remove Interface from Router Function "

    router_id = resource._get_resource_id(self,"ROUTER",router)
    if not router_id :
        return False

    subnet_id = resource._get_resource_id(self,"SUBNET",subnet)
    if not subnet_id :
        return False

    request = {"subnet_id": subnet_id}
    result = curl(self.controller + ':9696/v2.0/routers/'+ router_id + '/remove_router_interface', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username,self.password,self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '200', 'PUT', request)
    if not result :
        return False
    print "subnet is Removed from router"
    return result




