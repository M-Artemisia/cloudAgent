#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5


#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs 
#This module features are:
#     1) add an created image by Jenkins to Glance
#     2) list images on Glance
#     3) list flavers on Compute
#     4) install an insance on nova



from openstackAdaptor import *
import os
from subprocess import check_call
import subprocess

    
#Adaptor
#TODO: & Singletone Pattern
class openstackCliAdaptor(openstackAbstractAdaptor):
    """
    this pattern convert some interfaces of openstak classes. 
    like list images in glance and so on 
    """

    '''
    class __impl:
        """ Implementation of the singleton interface """
        
        def spam(self):
            """ Test method, return singleton id """
            return id(self)
    
    # storage for the instance reference
    __instance = None
    
    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if openstackCliAdaptor.__instance is None :
            openstackCliAdaptor.__instance = openstackCliAdaptor.__impl()
            self.__dict__['_Singleton__instance'] = Singleton.__instance
    '''

    def __init__(self, username, password, tenant, auth_url ):

        """
        create singletone instance
        @type username: Stirng 
        @param username: it is equivalent param --os-username for all of openstack commands  
        @type password: Stirng 
        @param password: it is equivalent param --os-password for all of openstack commands  
        @type tenant: Stirng 
        @param tenant: it is equivalent param --os-tenant-name for all of openstack commands  
        @type auth_url: Stirng 
        @param auth_url: it is equivalent param --os-auth-url for all of openstack commands  
        """

        
        username ="admin" 
        password = "xamin"
        tenant = "admin"
        auth_url = "http://10.1.48.25:35357/v2.0"

        self.username = '--os-username=' + username 
        self.password = '--os-password=' + password
        self.tenant = '--os-tenant-name='+ tenant
        self.auth_url = '--os-auth-url=' + auth_url

    def list_images(self):

        """
        list images on the Glance
        @rtype: List 
        @return: List of images on Glance
        """
        print "in list_image func....."
        images=subprocess.Popen(['glance', self.username, self.password,self.tenant,self.auth_url, 'image-list'],\
                  stdout=subprocess.PIPE).communicate()[0].split('\n')

        print ("Images are: ")
        for image in images:
            print (image)
    
        return images

        
    def list_flavors(self):

        """
        list existance flavers
        @rtype: List 
        @return: List of images on Glance
        """
        print "in list_flavor func....."
        flavors=subprocess.Popen(['nova', self.username, self.password,self.tenant,self.auth_url,'flavor-list'],\
                                 stdout=subprocess.PIPE).communicate()[0].split('\n')
                
        print ("Flavors are: ")
        for flavor in flavors: print (flavor)

        return flavors


    def install_image(self,instance_name, image='cirros-0.3.2-x86_64', flavor='m1.tiny', \
                      security_group = 'default', key_name = 'demo-key',nic = None):
        """
        install selected image with selected flavor
        @type instance_nam: stirng
        @param instance_nam: name of instance that should be run
        @type image: stirng
        @param image:  selected image name
        @type flavor: string
        @param flavor: selected flavor name
        @rtype: boolean
        @return: image installation status. if image installation fails, this function returns 0, otherwise returns 1 
        """
        #nova boot --flavor m1.tiny --image cirros-0.3.2-x86_64 --nic net-id=DEMO_NET_ID \
        #    --security-group default --key-name demo-key demo-instance1
        #tested by me
        #nova boot --flavor m1.tiny --image cirros-0.3.2-x86_64  --security-group default --key-name demo-key demo-instance1
        print "in install_image ....."
        exit_code = check_call(['nova', self.username, self.password,self.tenant,self.auth_url,\
                                'boot', '--flavor=' + flavor,'--image=' + image, '--security-group=' + security_group,'--key_name='+key_name, instance_name])
        return exit_code
    
        
        
    def get_vnc_url(self,instance):
        
        """
        finds the VNC url of the instance
        TODO: transfer VNC console of instance to webpage.
        @type arg1: string
        @param arg1: url of instance' VNC console 
        """
        print "in get_vnc_url func....."
        out=subprocess.Popen(['nova', self.username, self.password,self.tenant,self.auth_url,'get-vnc-console',instance, 'novnc'],\
                                 stdout=subprocess.PIPE).communicate()[0].split('\n')
        url = '';
        '''
        +-------+------------------------------------------------------------------------------------+
        | Type  | Url                                                                                |
        +-------+------------------------------------------------------------------------------------+
        | novnc | http://controller:6080/vnc_auto.html?token=2f6dd985-f906-4bfc-b566-e87ce656375b
        '''
        return 

        
    def register_to_image_db(self, appliance_spec, container, is_publich):
    
        """
        adds jenkins' created appliance to glance.
        @type arg1: dictionary
        @param arg1: a dictionary witch contains all of the specifications of appliance. specs r: ....
        """
        
        print "in register_to_glance func....."
        out=subprocess.Popen(['glance', self.username, self.password, self.tenant, sel.auth_url, 'image-create',\
                              '--name=' + appliance_spec['name'], '--disk-format=' + '.qcow2', '--container-format ' + container,\
                              '--is-public= ' + is_publich,'--copy-from ' + appliance_spec['url']],\
                              stdout=subprocess.PIPE).communicate()[0].split('\n')

        '''
         glance image-create --name=IMAGELABEL --disk-format=FILEFORMAT \
                            --container-format=CONTAINERFORMAT --is-public=ACCESSVALUE < IMAGEFILE
         glance image-create --name "cirros-0.3.2-x86_64" --disk-format qcow2 \
             --container-format bare --is-public True --progress --file cirros-0.3.2-x86_64-disk.img
        '''
        return 
