#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re
from curlWrapper import curl
import resource
import keystoneWrapper


def add_image(self, appliance_spec):
    
    print "in add image func....."
    
    header_list = ['X-Auth-Token: ' + keystoneWrapper.get_token(self, self.username,self.password,self.tenant),  'x-image-meta-disk_format: qcow2', 'x-image-meta-container_format: bare','x-image-meta-is_public: true']
    
    if appliance_spec['url'] == "None" or appliance_spec['name'] == "None" :
        print "Appliance Name & appliance URL can't be None!"
        return False
            
    header_list.append('x-glance-api-copy-from: ' + re.match(r'(.*).xvm2',appliance_spec['url']).group(1) + '.qcow2' )
    header_list.append('x-image-meta-name: ' + appliance_spec['name'])

    if appliance_spec["installed_size"] != "None" :
        header_list.append('x-image-meta-size: ' + appliance_spec["installed_size"])

    if appliance_spec["memory"] != "None" :
        header_list.append('x-image-meta-min_ram: ' + appliance_spec["memory"])

    if appliance_spec["storage"] != "None" :
        header_list.append('x-image-meta-min_disk: ' + appliance_spec["storage"])
 

    print "header list is: ", header_list
    result = curl(self.controller + ':9292/v1/images', header_list, '201', 'POST')

    if not result :
        return False
    image_id = result['image']['id']
    return {"image_id": image_id}
