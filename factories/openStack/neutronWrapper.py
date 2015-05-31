#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re
from curlWrapper import curl
from time import sleep

import resource
import keystoneWrapper, computeWrapper

#The code Checks to see if there is any free allocated ip for the tenant. if yes returns it and if no, allocates a new one.
def _generate_new_float_ip(self, user, password, project, tenant_id, pool):

    request = {"pool": pool}
    float_ip_id = ""
    associated = False
    
    result = computeWrapper.list_float_ips(self, user, password, project, tenant_id)  #you cannot list ips when token does not match the project.
    result['message'] = "Can list float ips : \n"+ str(result['message'])
    if result['status'] == "error" :
    	return result

    result = result['message']
    print "list of floating ips for tenenat ",tenant_id
    print result

    print "Trying to find free floating ips and associate one to the server"
	
    for i in range(0, len(result['floating_ips'])):
	if associated:
	    break
        if not result['floating_ips'][i]['fixed_ip']: #if no fixed_ip is there
            id = result['floating_ips'][i]['id']
	    ip = result['floating_ips'][i]['ip']
	    print "fixed ip none for id ", id
            # first we should see the details (to ensure it's status id DOWN)
            #res = get_floating_ip_detail(tenant_id, id, token)
            #print str(res) 
            #Returns No more info that what we had before :(

            # We can associate the ip to the server
            print "We are going to associate the ip ", ip
    	    return {"status" : "success" , "message" : ip }


    #if not associated, allocate a new IP:
    print "No free floating ips. Trying to allocate one.."
    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
					 str(token_res['message'])
  	return token_res    
    token = str(token_res['message'])
	
    result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips', \
    	['X-Auth-Token: ' + token ,\
        	'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'POST', request)
    if result['status'] == "error" :
	result['message'] = "Can not allocate new floating ip : \n"+ str(result['message'])
        return result

    #return result['message']['floating_ip']['ip']
    return {'status':'success', 'message': str(result['message']['floating_ip']['ip'])}

"""def _generate_new_float_ip(self, user, password, project, tenant_id, pool):

    
    request = {"pool": pool}
    result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips', \
                      ['X-Auth-Token: ' + token ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'POST', request)
    if not result :
        return False
        
    return result['floating_ip']['ip']
"""

def _assign_float_ip(self, user, password, project, external_ip_pool, server):

    import resource 
    print 
    print resource
    print type(resource)
    print


    tenant_id = resource._get_resource_id(self,"TENANT",project)
    if tenant_id['status'] == "error" :
        print "cant find the project ",tenant_id 
        tenant_id['message'] = "Cannot find tenant : "+ str(tenant_id['message'])
	return tenant_id
    #tenant_id = str(tenant_id['message'])
    tenant_id = tenant_id['message']
	
    float_ip = _generate_new_float_ip(self, user, password, project, tenant_id, external_ip_pool) 
    if float_ip['status'] == "error" :
	return float_ip
    float_ip = float_ip['message']
    
    request = {"addFloatingIp": {"address": str(float_ip)}} 
    #/v2/{tenant_id}/servers
    sleep(5)
    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
                                         str(token_res['message'])
        return token_res
    token = str(token_res['message'])
    #
    res = curl(self.controller + str(':8774/v2/' + tenant_id + '/servers'), \
                   ['X-Auth-Token: ' + token, "Accept: application/json",'Access-Control-Allow-Origin: *'], '200', 'GET')
           
    if res['status'] == "error":
        #print "cant find server list!"
	res['message'] ="Cannor find server list : " +str(res['message'])
        return res
    resources = res['message']['servers']

    server_id = ""
    for resource in resources :
        if server in resource['name'] :
            server_id = resource['id']

    if not server_id :
        print "There is no server with name %s on open stack!"  % (server)
        return {"status" : "error" , "message" : "There is no server with name "+server+" on open stack!"}
    #print "The ID of the  server, with name %s is  %s" % (str(server), str(server_id))


    result = curl(self.controller + str(':8774/v2/' + tenant_id + '/servers/' + server_id +'/action'), \
                      ['X-Auth-Token: ' + token ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'202', 'POST', request)
    #  -H "X-Auth-Project-Id: demo" -H "User-Agent: python-novaclient"
    if result['status'] == "error":
        print "Neutron ERROR......Error in associating float-ip with the server"
        return  {"status" : "error" , "message" : "Error in associating float-ip with the server: \n"+str(result['message'])}
    return {"status" : "success" , "message" : float_ip}

def add_network(self, user, password, project, external=False,network_name='xaas_int2'):
    """
    Create a network & a subnet for a specific project 
    """
    tenant_id = resource._get_resource_id(self,"TENANT", project);
    if tenant_id['status'] == "error" :
	print "cant find the project ",tenant_id
        tenant_id['message'] = "Cannot find tenant : "+ str(tenant_id['message'])
        return tenant_id
    #create_network
    request = {"network":{ \
            "tenant_id": tenant_id,\
                "name": network_name,\
                "admin_state_up": "true"}}
    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
                                         str(token_res['message'])
	return token_res
    token = str(token_res['message'])

    network = curl(self.controller + ':9696/v2.0/networks', \
                       ['X-Auth-Token: ' + token ,\
                            'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                       '201', 'POST', request)
    if network['status'] == "error" :
	network['message'] = "Can not add network : "+ str(network['message'])
        return network
    return network

def add_subnet(self, user, password, project, network_id ,subent_name='xaas_subnet',network_address='192.168.10.0/24'):
    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
                                         str(token_res['message'])
	return token_res
    token = str(token_res['message'])

    print "Creating SubNet..."
    request = {"subnet":{ \
            "name":subent_name,\
                "network_id": network_id ,\
                "ip_version":4,\
                "cidr": network_address}}
    subnet = curl(self.controller + ':9696/v2.0/subnets', ['X-Auth-Token: ' + token ,\
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if subnet['status'] == "error":
    	subnet['message'] = "Can not add subnet : "+ str(subnet['message'])
    	return subnet
    return subnet

def add_router(self, user, password, project, router_name, gateway='ext-net', internal_subnet='xaas_subnet'):
    """
    Create a new router for a specific project and introduce extenal_net as a gateway to it
    Also it adds internal_network as a interface to that.
    """

    #GET IP OF EXTERNAL NETWORK
    gateway_id = resource._get_resource_id(self,"NETWORK", gateway);
        #print "cant find gateway : ", gateway_id
    if gateway_id['status'] == "error":
	gateway_id['message'] = "Cannot find gateway " +str(gateway) +" : "+str(gateway_id['message']) 
	return gateway_id
    gateway_id = gateway_id['message']

    subnet_id = resource._get_resource_id(self,"SUBNET", internal_subnet)
    if subnet_id['status'] == "error":
        #print "cant find subnet", subnet_id
	subnet_id['message'] = "Cannot find subnet "+str(internal_subnet)+" : "+ str(subnet_id['message'])
        return subnet_id
    subnet_id = subnet_id['message']

    print "Creating Router...gateway=%s subnet=%s" %(gateway_id, subnet_id)
    
    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
                                         str(token_res['message'])
	return token_res
    token = str(token_res['message'])

    #CREATE Router
    request = {"router":{ \
            "name": router_name,\
                "external_gateway_info": {"network_id":gateway_id},\
                "admin_state_up":"true"}}
    router = curl(self.controller + ':9696/v2.0/routers', \ ['X-Auth-Token: ' + token , \
                           'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                      '201', 'POST', request)
    if router['status'] == "error" :
	router['message'] = "Failed to created router : "+ router['message']
        return router
            
    #ADD Interface
    result = _add_interface_to_router(self,user, password, project, router_name,internal_subnet)
    #if result['status'] == "error" :
    #	return result
    return result 

def _add_interface_to_router(self, user, password, project, router_name, internal_subnet ):
    print "Adding inetrface... "

    router_id = resource._get_resource_id(self,"ROUTER", router_name);
    if router_id['status'] == "error" : 
	router_id['message'] = "Cannot find router "+str(router_name) + " : " + str(router_id['message'])
	return router_id
    router_id = router_id['message']

    subnet_id = resource._get_resource_id(self,"SUBNET", internal_subnet)
    if subnet_id['status'] == "error":
        subnet_id['message'] = "Cannot find subnet "+str(internal_subnet)+" : "+ str(subnet_id['message'])
        return subnet_id
    subnet_id = subnet_id['message']

    request = {"subnet_id": subnet_id }

    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
 	token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
                                         str(token_res['message'])
        return token_res
    token = str(token_res['message'])

    interface = curl(self.controller + ':9696/v2.0/routers/'+ router_id + "/add_router_interface", \
                         ['X-Auth-Token: ' + token, 'Content-Type: application/json',\
				 'Accept: application/json','Access-Control-Allow-Origin: *'], '200', 'PUT', request)
    if interface['status'] == "error" :
	interface['message'] = "Failed to add interface to router :\n"+ str(interface['message'])
        return interface
    return interface


def remove_network(self, user, password, project, network):

    net_id = resource._get_resource_id(self,"NETWORK",network)
    if net_id['status'] == "error" :
	net_id['message'] = "Cannot find NETWORK "+str(network)+" : "+ str(net_id['message'])
        return net_id
    net_id = net_id['message']

    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
	token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
                                         str(token_res['message'])
        return token_res
    token = str(token_res['message'])

    result = curl(self.controller + ':9696/v2.0/networks/'+ str(net_id) , ['X-Auth-Token: + token ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '204', 'DELETE')
    if result['status'] == "error" :
	print "Failed to remove network"
	result['message'] = "Failed to remove network :\n" + str(result['message'])
        return result

    print "Network is removed"
    return result


def remove_subnet(self, user, password, project, subnet):

    subnet_id = resource._get_resource_id(self,"SUBNET",subnet)
    if subnet_id['status'] == "error" :
	subnet_id['message'] = "Cannot find subnet "+str(internal_subnet)+" : "+ str(subnet_id['message'])
        return subnet_id
    subnet_id = subnet_id['message']

    print "user pass and subnet in this project is: "
    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
                                         str(token_res['message'])
	return token_res
    token = str(token_res['message'])

    result = curl(self.controller + ':9696/v2.0/subnets/'+ str(subnet_id), ['X-Auth-Token: ' + token ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '204', 'DELETE')
    if result['status'] == "error" :
	print "Failed to remove SubNetwork"
	result['message'] = "Failed to remove Subnetwork :\n" + str(result['message'])
        return result
    print "subNetwork is removed"
    return result


def remove_router(self, user, password, project, router):
    print "Testing Remove Router Function "

    router_id = resource._get_resource_id(self,"ROUTER",router)
    if router_id['status'] == "error" :
	router_id['message'] = "Cannot find router "+str(router_name) + " : " + str(router_id['message'])
        return router_id
    router_id = router_id['message']

    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        return token_res
    token = str(token_res['message'])

    result = curl(self.controller + ':9696/v2.0/routers/'+ str(router_id), ['X-Auth-Token: ' + token ,\
                           'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                      '204', 'DELETE')
    if result['status'] == "error" :
	print "Failed to remove router"
	result['message'] = "Failed to remove router :\n" + str(result['message'])
        return result
    print "Router is removed"
    return result


def remove_interface_from_router(self, user, password, project, router, subnet):
    print "Testing Remove Interface from Router Function "

    router_id = resource._get_resource_id(self,"ROUTER",router)
    if router_id['status'] == "error" :
        router_id['message'] = "Cannot find router "+str(router) + " : " + str(router_id['message'])
        return router_id
    router_id = router_id['message']

    subnet_id = resource._get_resource_id(self,"SUBNET",subnet)
    if subnet_id['status'] == "error" :
        subnet_id['message'] = "Cannot find router "+str(subnet) + " : " + str(subnet_id['message'])
        return subnet_id
    subnet_id = subnet_id['message']	

    #Getting token:
    token_res = keystoneWrapper.get_token(self, user, password, project)
    if token_res['status'] == "error":
        #print "Error in getting token for user=%s, password=%s, project=%s " %(user, password, project)
        token_res['message'] = "Error in getting token for user="+user+", password="+password+", project="+project+ "\n"+ \
                                         str(token_res['message'])
	return token_res
    token = str(token_res['message'])

    request = {"subnet_id": str(subnet_id)}
    result = curl(self.controller + ':9696/v2.0/routers/'+ str(router_id) + '/remove_router_interface', \
		['X-Auth-Token: ' + token, 'Content-Type: application/json', 'Accept: application/json', \
			'Access-Control-Allow-Origin: *'],'200', 'PUT', request)
    if result['status'] == "error":
        print "Failed to remove subnet from router"
	result['message'] = "Failed to remove subnet from router :\n" + str(result['message'])
	return result
    print "subnet is Removed from router"
    return result



