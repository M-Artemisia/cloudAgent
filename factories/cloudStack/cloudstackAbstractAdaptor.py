#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

from abc import ABCMeta, abstractmethod


#This class is an adaptor for cloudstack.
#It connecets Clooudstack to Xamin GUIs 
#Features:
#     1) add an created image by Jenkins on ...
#     2) list images on ....
#     3) list flavers on ....
#     4) install an insance on....

#Adaptor Pattern
class cloudstackAbstractAdaptor():#cloudAdaptor
    """
    this pattern convert some interfaces of openstak classes. 
    like list images in glance and so on 
    """

    __metaclass__ = ABCMeta
        
    @abstractmethod
    def list_images(self): pass

    @abstractmethod        
    def list_flavors(self): pass

    @abstractmethod
    def install_image(self): pass    
        
    @abstractmethod
    def get_vnc_url(self): pass

    @abstractmethod    
    def register_to_image_db(self): pass
