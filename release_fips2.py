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

    return result

#Lists floating ips for a token
def list_float_ips(tenant_id, token):
    result = curl(controller +':8774/v2/' + tenant_id + '/os-floating-ips', \
                      ['X-Auth-Token: ' + token , 'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'GET')
    return result

#Error in this module
def get_floating_ip_detail(tenant_id, float_ip_id, token):
    result = curl('10.1.48.242:8774/v2/' + tenant_id + '/os-floating-ips/' + str(float_ip_id) , \
                      ['X-Auth-Token: ' + token , 'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'GET')
    return result


# id is the id of floating ip
def _deallocate_float_ip(tenant_id, id):
    print "ip id is ", id
    print "tenant id is ", tenant_id
    result = curl('10.1.48.242:8774/v2/' + tenant_id + '/os-floating-ips/' + str(id)  , \
                      ['X-Auth-Token: ' + token , 'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'202', 'DELETE')
    return result



if __name__ == '__main__':
    print "Hello! I am going to release free floating ips for this tenant :)"
    
    try:

    	#token = str(get_token("admin", "admin", "admin"))
    	result = get_token(user, passwd, tenant_name)
	if result['status'] == "error":
	    print result['message']
	exit

	token = str(result['message']['access']['token']['id'])
	print "token is  " ,token
    	print "tenant_id   ", tenant_id

    
    	result = list_float_ips(tenant_id, token)  #you cannot list ips when token does not match the project :)
    	if result['status'] == "error" :
            print result['message']
	    exit
	print "--list of floating ips for tenenat ",tenant_id
    	print result['message']
	result = result['message']

    
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
	    	res = _deallocate_float_ip(tenant_id, str(id))
		if res['status'] == "error":
		    print res['message']

    except: 
	print "exception occured"
