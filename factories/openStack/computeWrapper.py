#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re
from curlWrapper import curl
import resource
import keystoneWrapper, neutronWrapper


def install_server(self, user, password, project, instance_name, external_ip_pool, internal_ip_pool, security_group = 'default', image='cirros-2', flavor='m1.small'):
    '''
    Assumptions: the xaas_for_startup for flavor & external network is assigned by default
    TODO: i use int as internal_network_NAME. we shpuld find the name of the internal net based on router:external element of the network API
    '''
    print "STEP 1"
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

    result = curl(self.controller + ':8774/v2/' + resource._get_resource_id(self,"TENANT",project) + '/servers', \
                      ['X-Auth-Token: ' + keystoneWrapper.get_token(self, user, password, project ) ,\
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
        False

    print "STEP 6"

    octets = re.split('(.*)\.(.*)\.(.*)\.(.*)', network)
    print "the image is installed. its invalid_ip: %s and the valid_ip: 217.218.62.%s" %(network, str(octets[4:5].pop())); print; print #TEST
    print "STEP 7"

    return "217.218.62.%s",str(octets[4:5].pop())


def remove_server(self, user, password, project, instance_name, external_ip_pool, internal_ip_pool, security_group = 'default', image='cirros-2', flavor='m1.small'):
    return False
