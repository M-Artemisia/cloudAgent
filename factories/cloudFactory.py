#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#from openStack import openstackCliAdaptor,openstackRestAdaptor,openstackSdkAdaptor
from openStack import openstackRestAdaptor

#Factory method Pattern
class cloudFactory():
    """
    this pattern abtract factory class for create cloud adaptors
    """
    #it should be singletont too
    # Create based on class name:
    def factory(classType,params): #TODO: get variable number of params for diffrent constructor
        #return eval(type + "()")
        if classType == "openstackCli": return openstackCliAdaptor(params)
        
        if classType == "openstackRest": return openstackRestAdaptor.openstackRestAdaptor(params)
        if classType == "openstackSdk": return openstackSdkAdaptor(params)
        if classType == "cloudstack": return cloudstackImplAdaptor(params)
        assert 0, "Bad adaptor creation: " + classType
    factory = staticmethod(factory)
                    

