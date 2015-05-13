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
    
    print "STEP 1"
    print "flavor is: ", flavor
    internal_net_id = resource._get_resource_id(self,"NETWORK",internal_ip_pool)
    image_id = resource._get_resource_id(self,"IMAGE",image)
    flavor_id = resource._get_resource_id(self,"FLAVOR",flavor)
    print "STEP 2"

    if not internal_net_id or not image_id or not flavor_id :
        print "internal_net_id=%s, image_id=%s, flavor_id=%s" %(internal_net_id, image_id, flavor_id)
        return False

    request = {"server":{ \
            "name": instance_name,\
                "imageRef": image_id,\
                "flavorRef": flavor_id,\
                "networks": [{"uuid": internal_net_id }],\
                "security_groups": [{"name": security_group}]}}
    print "STEP 3"

    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if not tenant_id:
        return False
    if not keystoneWrapper.get_token(self, user, password, project) :
        print "user, password, project ", user, password, project
        return False

    result = curl(self.controller + ':8774/v2/' + tenant_id + '/servers', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '202', 'POST', request)
    print "STEP 4"
    if not result :
        print "install server result is false"
        return False

    print "STEP 5"
    #sleep(10)
    network = neutronWrapper._assign_float_ip(self, user, password, project, external_ip_pool, instance_name)
    if not network:
        print "STEP 6"
        return False

    print "STEP 6"

    octets = re.split('(.*)\.(.*)\.(.*)\.(.*)', network)
    print "the image is installed. its invalid_ip: %s and the valid_ip: 217.218.62.%s" %(network, str(octets[4:5].pop())); print; print #TEST
    print "STEP 7"

    return "217.218.62."+str(octets[4:5].pop())


def remove_server(self, user, password, project, server):

    print "Testing Remove Server Function "

    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if not tenant_id :
        return False

    print "STEP 1: tenant_id is ",tenant_id 

    #server_id = resource._get_resource_id(self,"SERVER",server, self.username, self.password, self.tenant)
    server_id = resource._get_resource_id(self,"SERVER",server, user, password, project)
    #server_id = resource._get_resource_id(self,"SERVER",server,project)
    if not server_id :
        return False


    #----- Added to get float_ip associated with the server
    #The code works when there is only one floating_ip in the tenant. 
    #In demo, the server and the ip associated to it, are created in their tenant. so it's ok to just retrun the first entry of the curl result :)
    print "STEP 2: release float ip"
    #1_"getting the float ip id"
    #float_ip_id = resource._get_floatip_id(self,"FLOATIP", tenant_id, user, password, project)
    float_ip_id = ""
    float_ip = ""
    result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips', \
                          ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                               'Accept: application/json', 'Access-Control-Allow-Origin: *'], '200', 'GET')
    if not result:
	print "No floating ip found for the tenant_id"
    else:
    	print "floating_ips for the tenant : ", result
        try:
	    float_ip_id = result['floating_ips'][0]['id']
	    float_ip = result['floating_ips'][0]['ip']
	    print float_ip
	    print "id: ", float_ip_id
	except:
	    print "Something is wrong with float ip - the id could not be found"
    

    if float_ip_id and not float_ip_id.isspace():  #if float_ip_id != "":
        try:
 	    #"2_removing the float ip from the server"
    	    request = {"removeFloatingIp": {"address": str(float_ip)}}
    	    result = curl(self.controller + ':8774/v2/' + tenant_id + '/servers/' + str(server_id) +'/action', \
            	['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                    'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], '202', 'POST',request)
	    #deallocate_float_ip(self, user, password, project, tenant_id, id)
    	    if not result:
        	print "Cannot disassociate floating ip from the server"
    	    else:
        	print "Floating ip disassociated from the server"
   	    

	    #3_deallocating float ip - DO NOT USE ADMIN TOKEN! You can only deallocate ips allocated to a tenant using the token for that tenant!!
            """ipresult = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips/' + str(float_ip_id) , \
                        ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                                'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      	'202', 'DELETE')"""
	    ipresult = deallocate_float_ip(self, user, password, project, tenant_id, str(float_ip_id))
	    print "ipresult (deallocate) : ", ipresult
	    if not ipresult :
                print "STEP 2: Cannot deallocate floating IP from the server!!--"
                #return False #We don't retrun Flase here
            else :
                print "STEP 2: Floating ip deallocated"
        except:
            print "STEP 2: Cannot deallocate floating IP from the server!!--"  # We Don't return false
     	    

    print "STEP 3: server_id is ", server_id

    request = '{"force_delete": null}'    
    
    result = curl(self.controller + ':8774/v2/'+ tenant_id + '/servers/' + server_id, \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '204', 'DELETE')
    
    print " ************************************************* "
    #print self.controller + ':8774/v2/'+ tenant_id + '/servers/' + server_id +'HEADERS: X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username, self.password, self.tenant) + '  -H Content-Type: application/json'+'  -H Accept: application/json   '+'  -H Access-Control-Allow-Origin: *'+'  204', '  DELETE'
    print "STEP 3: result is ", result
    if not result :
  	return False
    print "server is removed"
    return result 


def add_flavor(self, user, password, project, flavor_name, ram, vcpus, disk):
    #ram based on M, disk Based on G
    print "Testing Flavor Add Function "
    tenant_id = resource._get_resource_id(self,"TENANT",self.tenant)
    if not tenant_id :
        return False
    request = {"flavor": {"name": flavor_name, "ram": ram, "vcpus" : vcpus, "disk" : disk ,"id": time.strftime("%Y%m%d_%H%M%S", time.gmtime()) }}
    result = curl(self.controller + ':8774/v2/'+ tenant_id + '/flavors', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username,self.password,self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '200', 'POST', request)
    if not result :
        return False
    print "flavor is added"
    return result


def remove_flavor(self, user, password, project,flavor):

    print "Testing Flavor Remove Function "
    tenant_id = resource._get_resource_id(self,"TENANT",self.tenant)
    if not tenant_id :
        return False

    flavor_id = resource._get_resource_id(self,"FLAVOR",flavor)
    if not flavor_id :
        return False

    result = curl(self.controller + ':8774/v2/'+ tenant_id + '/flavors/' + flavor_id, \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username, self.password, self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '202', 'DELETE')
    if not result :
        return False
    print "flavor is removed"
    return result


#Added by jabbari -only ips for that project could be deallocated
def deallocate_float_ip(self, user, password, project, tenant_id, id):
    #print "id is ", id
    #print "tenant id is ", tenant_id
    result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips/' + str(id)  , \
                ['X-Auth-Token: ' + keystoneWrapper.get_token( self, user, password, project ),\
                        'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'202', 'DELETE')
    if not result :
        print "--deallocate False--"
        return False

    return True

#added by jabbari
def list_float_ips(self, user, password, project, tenant_id):
    result = curl('10.1.48.242:8774/v2/' + tenant_id + '/os-floating-ips', \
                      ['X-Auth-Token: '  + keystoneWrapper.get_token( self, user, password, project ) , 'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'GET')
    if not result :
        return False

    return result



