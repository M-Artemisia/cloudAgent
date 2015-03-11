#!/usr/bin/pythyon
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re
from openstackAbstractAdaptor import openstackAbstractAdaptor

import resource
import keystoneWrapper, neutronWrapper, computeWrapper, glanceWrapper

class openstackRestAdaptor(openstackAbstractAdaptor):
    """
    this pattern convert some interfaces of openstak classes. 
    like list images in glance and so on 
    """

    def __init__(self, params ):

        self.username = params["username"]
        self.password = params["password"]
        self.tenant = params["tenant"]
        self.controller = params["controller"]
        self.admin_token = keystoneWrapper.get_token(self, self.username,self.password,self.tenant)

        self.admin_role_id= resource._get_resource_id(self,"TENANT",'admin')
        self.member_role_id= resource._get_resource_id(self,"ROLE","_member_")

        if not self.admin_role_id or not self.member_role_id :
            print "It seems the Openstack has not correct roles for admin and _member_"
            return False


    def add_user(self,name, password,project):       
        return keystoneWrapper.add_user(self,name, password,project)

    def remove_user(self,username):
        return keystoneWrapper.remove_user(self,username)


    def add_tenant(self, name, desc, ram, vcpu, instances):
        return keystoneWrapper.add_tenant(self, name, desc, ram, vcpu, instances)


    def remove_tenant(self, project_name):
        return keystoneWrapper.remove_tenant(self, project_name)
    

    def add_image(self, appliance_spec):
            return glanceWrapper. add_image(self, appliance_spec)
 
    def install_server(self, user, password, project, instance_name, external_ip_pool, internal_ip_pool, security_group = 'default', image='cirros-2', flavor='m1.small'):
        '''
        Assumptions: the xaas_for_startup for flavor & external network is assigned by default
        TODO: i use int as internal_network_NAME. we shpuld find the name of the internal net based on router:external element of the network API
        '''
        return computeWrapper.install_server(self, user, password, project, instance_name, external_ip_pool, internal_ip_pool, security_group, image, flavor)

    def add_network(self, user, password, project, external=False,network_name='xaas_int2', subent_name='xaas_subnet',network_address='192.168.10.0/24'):
        """
        Create a network & a subnet for a specific project 
        """
        return neutronWrapper.add_network(self, user, password, project, external,network_name, subent_name,network_address)


    def add_router(self, user, password, project, router_name, gateway='ext-net', internal_subnet='xaas_subnet'):
        """
        Create a new router for a specific project and introduce extenal_net as a gateway to it
        Also it adds internal_network as a interface to that.
        """
        return neutronWrapper.add_router(self, user, password, project, router_name, gateway, internal_subnet)

