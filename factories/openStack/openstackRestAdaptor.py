#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, sys, re
from curly import curl
from openstackAbstractAdaptor import openstackAbstractAdaptor
import resource_info
from time import sleep

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
        self.admin_token = self.get_token(self.username,self.password,self.tenant)

        self.admin_role_id= self._get_resource_id("TENANT",'admin')
        self.member_role_id= self._get_resource_id("ROLE","_member_")

        if not self.admin_role_id or not self.member_role_id :
            print "It seems the Openstack has not correct roles for admin and _member_"
            return False


    def get_token(self,username,password,tenant  ):

        request = {"auth": {"tenantName": tenant  , "passwordCredentials": {"username": username  , "password": password }}}
        result = curl(self.controller + ':5000/v2.0/tokens', ['Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], '200', 'POST', request)

        return str(result['access']['token']['id'])


    def add_user(self,name, password,project):
        
        tenant_id = self._get_resource_id("TENANT",project)
        if not tenant_id :
            return False
        request = {"user": {"name": name , "password": password, "email" : name, "default_project_id": tenant_id }}
        result = curl(self.controller + ':5000/v3/users', \
                                      ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant) ,\
                                       'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'], \
                                      '201', 'POST', request)
        if not result :
            return False
        return result 


    def add_user_role(self, username, project):
        
        tenant_id = self._get_resource_id("TENANT",project)
        if not tenant_id :
            return False

        user_id = self._get_resource_id("USER",username)
        if not user_id :
            return False

        result = curl(self.controller + ':5000/v3/projects/' + str(tenant_id) + '/users/' + str(user_id) + '/roles/' + str(self.member_role_id) , \
                                      ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), 'Content-Type: application/json','Access-Control-Allow-Origin: *'], '204', 'PUT')

        if not result :
            return False
        return result 

    def remove_user(self,username):

        user_id = self._get_resource_id("USER",username)
        if not user_id:
            return False

        result = curl(self.controller + ':5000/v3/users/' + user_id, \
                                          ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant)], \
                                          '204', 'DELETE')
        if not result:
            return False
        return result


    def add_tenant(self, name, desc, ram, vcpu, instances):

        #*******ADDING TENANT******
        request = {"project": {"description": desc , "enabled": True , "name": name, "domain_id" : "default" }}
        result = curl(self.controller + ':5000/v3/projects', \
                                      ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant) ,\
                                       'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                                      '201', 'POST', request)
        if not result :
            return False

        #*******ADDING QUOTA******
        current_tenant_id = result['project']['id'];
        admin_tenant_id = self._get_resource_id("TENANT","admin");
        
        request = {"quota_set": {"cores": vcpu , "instances": instances , "ram": ram }}
        result = curl(self.controller + ':8774/v2/' + str(admin_tenant_id) + '/os-quota-sets/' + str(current_tenant_id), \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant),'Content-Type: application/json', "Accept: application/json",'Access-Control-Allow-Origin: *'], '200', 'PUT', request)
        if not result :
            return False        
        return True


    def remove_tenant(self, project_name):

        if project_name is None :
            print "project name cant be Null"
            return False

        tenant_id = self._get_resource_id("TENANT",project_name)
        if not tenant_id:
            return False

        result = ""
        result = curl(self.controller + ':5000/v3/projects/' + str(tenant_id), \
                                          ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), "Accept: application/json",'Access-Control-Allow-Origin: *'], '204', 'DELETE')
        if not result:
            return False
        return result
    

    def add_image(self, appliance_spec):
    
        print "in add image func....."

        header_list = ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant),  'x-image-meta-disk_format: qcow2', 'x-image-meta-container_format: bare','x-image-meta-is_public: true']

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


    def install_server(self, user, password, project, instance_name, external_ip_pool, internal_ip_pool, security_group = 'default', image='cirros-2', flavor='m1.small'):
        '''
        Assumptions: the xaas_for_startup for flavor & external network is assigned by default
        TODO: i use int as internal_network_NAME. we shpuld find the name of the internal net based on router:external element of the network API
        '''
        print "STEP 1"
        internal_net_id = self._get_resource_id("NETWORK",internal_ip_pool)
        image_id = self._get_resource_id("IMAGE",image)
        flavor_id = self._get_resource_id("FLAVOR",flavor)
        print "STEP 2"

        if not internal_net_id or not image_id or not flavor_id :
             print "internal_net_id=%s, image_id=%s, flavor_id=%s" %(internal_net_id, image_id, flavor_id)
             return False

        request = {"server":{ \
           "name": instance_name,\
           "imageRef": image_id,\
           "flavorRef": flavor_id,\
           "networks": [{"uuid": internal_net_id }],\
           "security_groups": [{"name": security_group}]}}
        print "STEP 3"

        result = curl(self.controller + ':8774/v2/' + self._get_resource_id("TENANT",project) + '/servers', \
                                      ['X-Auth-Token: ' + self.get_token( user, password, project ) ,\
                                       'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                                      '202', 'POST', request)
        print "STEP 4"
        if not result :
            print "install server result is false"
            return False

        print "STEP 5"

        float_ip = self._generate_new_float_ip(user, password, project, external_ip_pool) 
        print "STEP 6"

        if not self._assign_float_ip(user, password, project, float_ip, instance_name) :
            print "STEP 7"
            False

        print "STEP 7"

        octets = re.split('(.*)\.(.*)\.(.*)\.(.*)', float_ip)
        print "the image is installed. its invalid_ip: %s and the valid_ip: 217.218.62.%s" %(float_ip, str(octets[4:5].pop())); print; print #TEST
        print "STEP 9"

        return "217.218.62.%s",str(octets[4:5].pop())



    def _generate_new_float_ip(self, user, password, project, pool):
        
        tenant_id = self._get_resource_id("TENANT",project)
        if not tenant_id :
            return False

        request = {"pool": pool}
        result = curl(self.controller + ':8774/v2/' + tenant_id + '/os-floating-ips', \
                                      ['X-Auth-Token: ' + self.get_token(user, password, project) ,\
                                       'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'200', 'POST', request)
        if not result :
            return False
        
        return result['floating_ip']['ip']


    def _assign_float_ip(self, user, password, project, float_ip, server):

        tenant_id = self._get_resource_id("TENANT",project)
        if not tenant_id :
            print "cant find the project ",tenant_id 
            return False

        #server_id = self._get_resource_id("SERVER",server)
        #if not server_id :
        #    return False

        request = {"addFloatingIp": {"address": float_ip}} 

        #/v2/{tenant_id}/servers
        sleep(5)
        res = curl(self.controller + str(':8774/v2/' + tenant_id + '/servers'), \
                      ['X-Auth-Token: ' + self.get_token(user, password, project), "Accept: application/json",'Access-Control-Allow-Origin: *'], '200', 'GET')
           
        if not res:
            print "cant find server list!"
            return False
        resources = res['servers']

        server_id = ""
        for resource in resources :
            if server in resource['name'] :
                server_id = resource['id']

        if not server_id :
            print "There is not server  with name %s on open stack!"  % (server)
            return False
        #print "The ID of the  server, with name %s is  %s" % (str(server), str(server_id))


        x= self.controller + ':8774/v2/' + tenant_id + '/servers/' + server_id +'/action'
        y= 'X-Auth-Token: ' + self.get_token(user, password, project)+' Content-Type: application/json ', 'Accept: application/json '+'Access-Control-Allow-Origin: *';
        #print "THE CURL IS: ...................."
        #print x;print y; print request
        result = curl(self.controller + str(':8774/v2/' + tenant_id + '/servers/' + server_id +'/action'), \
                                      ['X-Auth-Token: ' + self.get_token(user, password, project) ,\
                                       'Content-Type: application/json', 'Accept: application/json', 'Access-Control-Allow-Origin: *'],'202', 'POST', request)
        #  -H "X-Auth-Project-Id: demo" -H "User-Agent: python-novaclient"
        if not result :
            print "ERROR.................."
            return False
        return result 




    def add_network(self, user, password, project, external=False,network_name='xaas_int2', subent_name='xaas_subnet',network_address='192.168.10.0/24'):
        """
        Create a network & a subnet for a specific project 
        """
        tenant_id = self._get_resource_id("TENANT", project);
        if not tenant_id :
            return False
        #create_network
        request = {"network":{ \
                               "tenant_id": tenant_id,\
                               "name": network_name,\
                               "admin_state_up": "true"}}
        network = curl(self.controller + ':9696/v2.0/networks', \
                                      ['X-Auth-Token: ' + self.get_token( user, password, project ) ,\
                                       'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                                      '201', 'POST', request)
        if not network :
            return False

        #create_subnet
        print "Creating SubNet..."
        request = {"subnet":{ \
                              "name":subent_name,\
                              "network_id": network['network']['id'],\
                              "ip_version":4,\
                              "cidr": network_address}}
        subnet = curl(self.controller + ':9696/v2.0/subnets', \
                                      ['X-Auth-Token: ' + self.get_token( user, password, project ) ,\
                                       'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                                      '201', 'POST', request)
        if not subnet :
            return False

        return True


    def add_router(self, user, password, project, router_name, gateway='ext-net', internal_subnet='xaas_subnet'):
        """
        Create a new router for a specific project and introduce extenal_net as a gateway to it
        Also it adds internal_network as a interface to that.
        """

        #GET IP OF EXTERNAL NETWORK
        gateway_id = self._get_resource_id("NETWORK", gateway);
        subnet_id=self._get_resource_id("SUBNET", internal_subnet)
        if not gateway_id or not subnet_id :
            print "cant find gateway=%s or subnet=%s" %(gateway_id,subnet_id)
            return False

        print "Creating Router...gateway=%s subnet=%s" %(gateway_id, subnet_id)
        #CREATE Router
        request = {"router":{ \
                "name": router_name,\
                "external_gateway_info": {"network_id":gateway_id},\
                "admin_state_up":"true"}}
        router = curl(self.controller + ':9696/v2.0/routers', \
                                      ['X-Auth-Token: ' + self.get_token( user, password,project ) ,\
                                       'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                                      '201', 'POST', request)
        if not router :
            return False
            
        #ADD Interface
        self. _add_interface_to_router(user, password, project, router_name,internal_subnet)
        return True

    def _add_interface_to_router(self, user, password, project, router_name, internal_subnet ):
        print "Adding inetrface... "
        router_id = self._get_resource_id("ROUTER", router_name);
        subnet_id = self._get_resource_id("SUBNET", internal_subnet)
        request = {"subnet_id": subnet_id }
        interface = curl(self.controller + ':9696/v2.0/routers/'+ router_id + "/add_router_interface", \
                                      ['X-Auth-Token: ' + self.get_token( user, password, project ) ,\
                                       'Content-Type: application/json', 'Accept: application/json','Access-Control-Allow-Origin: *'], \
                                      '200', 'PUT', request)
        if not interface :
            return False
            
        return True

    #************************GET RESOURCED ID**************************
    #TODO: Get Any Info That the User Need IT
    def _get_resource_id(self, resource_type, resource_name):
        
        def _resources_list(client_type, response_code):
            result = curl(self.controller + str(client_type), \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), "Accept: application/json",'Access-Control-Allow-Origin: *'], response_code, 'GET')
            if not result :
                return False
            return result

        resources = []
        if resource_type == "TENANT":            
            res = _resources_list(':5000/v3/projects', '200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res["projects"]

        elif resource_type == "USER":
            res = _resources_list(':5000/v3/users','200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res['users']
        
        elif resource_type == "ROLE":
            res = _resources_list(':5000/v3/roles','200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res['roles']

        elif resource_type == "FLAVOR":
            #/v2/{tenant_id}/flavors
            res = _resources_list(':8774/v2/' + self._get_resource_id("TENANT", 'admin') + '/flavors','200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res['flavors']

        elif resource_type == "IMAGE":
            #/v2/{tenant_id}/images
            res = _resources_list(':8774/v2/' + self._get_resource_id("TENANT", 'admin') + '/images','200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res['images']
        elif resource_type == "SERVER":
            #/v2/{tenant_id}/servers
            res = _resources_list(':8774/v2/' + self._get_resource_id("TENANT", 'DemoTest') + '/servers','200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res['servers']

        elif resource_type == "NETWORK":
            res = _resources_list(':9696/v2.0/networks','200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res['networks']

        elif resource_type == "Network":
            res = _resources_list(':9696/v2.0/networks','200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res['networks']

        elif resource_type == "SUBNET":
           res = _resources_list(':9696/v2.0/subnets','200')
           if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
           resources = res['subnets']

        elif resource_type == "ROUTER":
            res = _resources_list(':9696/v2.0/routers','200')
            if not res:
                print "There is not any %s on Openstack!" %(resource_type)
                return False
            resources = res['routers']

        else:
            print "The %s resource is not supported..." %(resource_type)
            return False 

        resource_id = ""
        for resource in resources :
            if resource_name == resource['name'] :
                resource_id = resource['id']

        if not resource_id :
            print "There is not resource %s with name %s on open stack!"  % (resource_type,resource_name)
            return False

        return str(resource_id)



