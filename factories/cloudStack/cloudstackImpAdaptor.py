#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5


#This module is an adaptor for cloudstack.
#It connecets Cloudstack to Xamin GUIs 
#This module features are:
#     1) add an created image by Jenkins
#     2) list images 
#     3) list flavers
#     4) install an insance
#     5) ...


import os
from subprocess import check_call
import subprocess
form cloudFactory import cloudstackAbstratctAdaptor

#Adaptor Pattern
class cloudstackImplAdaptor(cloudstackAbstratctAdaptor):
    """
    this pattern convert some interfaces of openstak classes. 
    like list images in glance and so on 
    """

    def __init__(self, .... ):

        """
        @type :
        @param :
        """
        return 
        
    def list_images(self):

        """
        list images on the Glance
        @rtype: 
        @return: 
        """
        return

        
    def list_flavors(self):

        """
        list existance flavers
        @rtype: List 
        @return: List of images on Glance
        """
        return


    def install_image(self,... ):
        """
        install selected image with selected flavor
        @type
        @param
        @rtype: 
        @return:
        """
        return
    
        
        
    def get_vnc_url(self,instance):
        
        """
        finds the VNC url of the instance
        TODO: transfer VNC console of instance to webpage.
        @type arg1: string
        @param arg1: url of instance' VNC console 
        """
        return 

        
    def register_to_iamge_db(self, appliance_spec, container, is_publich):
    
        """
        adds jenkins' created appliance to
        @type arg1: dictionary
        @param arg1: a dictionary witch contains all of the specifications of appliance. specs r: ....
        """        
        return 
