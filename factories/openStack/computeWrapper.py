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

    network = neutronWrapper._assign_float_ip(self, user, password, project, external_ip_pool, instance_name)
    if not network:
        print "STEP 6"
        return False

    print "STEP 6"

    octets = re.split('(.*)\.(.*)\.(.*)\.(.*)', network)
    print "the image is installed. its invalid_ip: %s and the valid_ip: 217.218.62.%s" %(network, str(octets[4:5].pop())); print; print #TEST
    print "STEP 7"

    return "217.218.62.%s",str(octets[4:5].pop())


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

    print "STEP 2: server_id is ", server_id

    request = '{"force_delete": null}'
    
    result = curl(self.controller + ':8774/v2/'+ tenant_id + '/servers/' + server_id, \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '204', 'DELETE')

    print " ************************************************* "
    print self.controller + ':8774/v2/'+ tenant_id + '/servers/' + server_id +'HEADERS: X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username, self.password, self.tenant) + '  -H Content-Type: application/json'+'  -H Accept: application/json   '+'  -H Access-Control-Allow-Origin: *'+'  204', '  DELETE'
    '''
    result = curl(self.controller + ':8774/v2.1/servers/' + server_id+'/action', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self,self.username, self.password, self.tenant) ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '202', 'POST',request)
    '''
    print "STEP 3: result is ", result 
    if not result :
        return False
    print "flavor is removed"
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
