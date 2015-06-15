#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

from abc import ABCMeta, abstractmethod

#This class is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs 
#features:
#     1) add an created image by Jenkins to Glance
#     2) list images on Glance
#     3) list flavers on Compute
#     4) install an insance on nova


#Abstract Class: Adaptor Pattern 
class openstackAbstractAdaptor(object):
    """
    this pattern convert some interfaces of openstak classes. 
    like list images in glance and so on 
    """

    __metaclass__ = ABCMeta
        
    @abstractmethod
    def add_user(self,name, password,project): pass
    
    @abstractmethod
    def remove_user(self,username): pass

#   @abstractmethod
#    def list_users(self): pass

    @abstractmethod
    def add_tenant(self, name, desc, ram, vcpu, instances): pass
    
    @abstractmethod
    def remove_tenant(self, project_name): pass

    @abstractmethod
    def add_image(self, appliance_spec): pass

    """
    @abstractmethod
    def list_images(self): pass

    @abstractmethod        
    def list_flavors(self): pass

    @abstractmethod
    def install_image(self,instance_name, image='cirros-0.3.2-x86_64', flavor='m1.tiny', \
                      security_group = 'default', key_name = 'demo-key',nic = None): pass    
        
    @abstractmethod
    def get_vnc_url(self,instance): pass

    """
    
