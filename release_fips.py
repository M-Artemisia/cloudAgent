#!/usr/bin/python
#Auther: Fatemeh Jabbari

#This module is a helper to free allocated floating ips for a tenant which are not bound to a fixed_ip
# Needs module curlWrapper 


#Config
controller = "10.1.48.242"
#token = str(get_token("admin", "admin", "admin"))
user = "xaas"   #for XAAS_VPS project
passwd = "xaas" #for XAAS_VPS project
tenant_name = "XAAS_VPS"  #"admin" for admin project
tenant_id = "d42627c7e28043e1adb6f6d128c630df" #XAAS_VPS    #"fe382a0e37f94ba5bc70980939979407" for admin project

import os, sys, re
from curlWrapper import curl


def get_token(username,password,tenant):

    request = {"auth": {"tenantName": tenant  , "passwordCredentials": {"username": username  , "password": password }}}
    result = curl(controller + ':5000/v2.0/tokens', ['Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], '200', 'POST', request)

    if not result:
        print "KEYSTONE:   ************************************************************************************"
        print "request: ", request
        print 'CurL: 10.1.48.242:5000/v2.0/tokens   ' + 'Content-Type: application/json    ' + 'Accept: application/json    ' + 'Access-Control-Allow-Origin: *    ' + '200'+ '   POST'
        print "Result: ", result
        return False
    return str(result['access']['token']['id'])


#Lists floating ips for a token
def list_float_ips(tenant_id, token):
    result = curl(controller +':8774/v2/' + tenant_id + '/os-floating-ips', \
                      ['X-Auth-Token: ' + token , 'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'GET')
    if not result :
        return False

    return result #-- DON'T CAST IT TO STR!!!!!

#Error in this module
def get_floating_ip_detail(tenant_id, float_ip_id, token):
    result = curl('10.1.48.242:8774/v2/' + tenant_id + '/os-floating-ips/' + str(float_ip_id) , \
                      ['X-Auth-Token: ' + token , 'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'GET')
    if not result :
        return False
    return result

# id is the id of floating ip
def _deallocate_float_ip(tenant_id, id):
    print "ip id is ", id
    print "tenant id is ", tenant_id
    result = curl('10.1.48.242:8774/v2/' + tenant_id + '/os-floating-ips/' + str(id)  , \
                      ['X-Auth-Token: ' + token , 'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'202', 'DELETE')
    if not result :
   	print "--deallocate False--"
        return False

    return True


if __name__ == '__main__':
    print "Hello! I am going to release free floating ips for this tenant :)"
    
    #token = str(get_token("admin", "admin", "admin"))
    token = str(get_token(user, passwd, tenant_name))
    print "token is  " ,token
    print "tenant_id   ", tenant_id
    #if _deallocate_float_ip(tenant_id, "067568f1-23ed-46c7-ae37-594de5919221"):
    #	print "ip deallocated"

    result = list_float_ips(tenant_id, token)  #you cannot list ips when token does not match the project :)
    print "--list of floating ips for tenenat ",tenant_id
    print result

    
    for i in range(0, len(result['floating_ips'])):
	if not result['floating_ips'][i]['fixed_ip']:
	    print "fixed ip none for id ", result['floating_ips'][i]['id']
	    id = result['floating_ips'][i]['id']	
            ip = result['floating_ips'][i]['ip']
 	    print "ip : ", ip

	    # first we should see the details (to ensure it's status id DOWN)
	    #res = get_floating_ip_detail(tenant_id, id, token)
            #print str(res) 
 	    #Returns No more info that what we had before :(
	    _deallocate_float_ip(tenant_id, str(id))
