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
import keystoneWrapper


def _generate_new_float_ip(self, user, password, project, tenant_id, pool):

    request = {"pool": pool}
    result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'POST', request)
    if not result :
        return False
        
    return result['floating_ip']['ip']


def _assign_float_ip(self, user, password, project, external_ip_pool, server):

    global resource 
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



def add_network(self, user, password, project, external=False,network_name='xaas_int2', subent_name='xaas_subnet',network_address='192.168.10.0/24'):
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

    #create_subnet
    print "Creating SubNet..."
    request = {"subnet":{ \
            "name":subent_name,\
                "network_id": network['network']['id'],\
                "ip_version":4,\
                "cidr": network_address}}
    subnet = curl(self.controller + ':9696/v2.0/subnets', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token( self, user, password, project ) ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if not subnet :
        return False

    return True


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




def remove_network(self, user, password, project, external=False,network_name='xaas_int2', subent_name='xaas_subnet',network_address='192.168.10.0/24'):
    #Remove dcpAgent
    #remove network:dhcp port, compute:None port, delete router, sunbet, net
    return False




def remove_router(self, user, password, project, router_name, gateway='ext-net', internal_subnet='xaas_subnet'):
    return False

def _remove_interface_from_router(self, user, password, project, router_name, internal_subnet ):
    return False
