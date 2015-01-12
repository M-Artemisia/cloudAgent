#!/usr/bin/python
#Auther: Mali Asemani, ml.asemani@gmail.com
#Date: 14-Nov-5

#This module is an adaptor for openstack.
#It connecets Openstack to Xamin GUIs like Market 
#Features:


import os, re
import sys
import curl

class openstackRestAdaptor():
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
        #TEST MALI
        self.__list_roles()

    def get_token(self,username,password,tenant ):

        request = {"auth": {"tenantName": tenant  , "passwordCredentials": {"username": username  , "password": password }}}
        result = curl.curl(self.controller + ':5000/v2.0/tokens', ['Content-Type: application/json', 'Accept: application/json'], '200', 'POST', request)
       
        if not result :
            return False
        return result['access']['token']['id']


    def add_user(self,name, password,project):
        
        tenants = self. __tenants_list()
        if not tenants :
            return False
        tenant_id = "" 
        for tenant in tenants :
            if tenant['name'] == project :
                tenant_id = tenant['id']

        request = {"user": {"name": name , "password": password, "email" : name, "default_project_id": tenant_id }}
        result = curl.curl(self.controller + ':5000/v3/users', \
                                      ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant) ,\
                                       'Content-Type: application/json', 'Accept: application/json'], \
                                      '201', 'POST', request)
        if not result :
            return False
        print "the added user is: "; print result; print; print #TEST
        return True

    def add_user_role(self, username, project):

        print "add user role.......", username, project
        tenants = self. __tenants_list()
        if not tenants :
            return False

        tenant_id = "" 
        for tenant in tenants :
            if tenant['name'] == project :
                tenant_id = tenant['id']

        if tenant_id == "":
            print "There is not such project in open stack users!"
            return False

        users = self.list_users()
        if not users :
            return False
        user_id = ""
        for user in users :
            if username == user['name'] :
                user_id = user['id']
        if user_id == "":
            print "There is not such user in open stack users!"
            return False

        print "userid=%s and project_id=%s member_role=%s" % (user_id, tenant_id, self.member_role_id)
        result = curl.curl(self.controller + ':5000/v3/projects/' + tenant_id + '/users/' + user_id + '/roles/' + self.member_role_id , \
                                      ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), 'Content-Type: application/json'], '204', 'PUT')

        if not result :
            return False
        print "the role is added to  user ", username; print result; print; print #TEST
        return True


    def remove_user(self,username):

        users = self.list_users()
        if not users :
            return False
        user_id = ""
        for user in users :
            if username == user['name'] :
                user_id = user['id']
        if user_id == "":
            print "There is not such user in open stack users!"
            return False
        print "Remove User: name = %s id = %s " % (username, user_id) ; print; print ##TEST 
        result = curl.curl(self.controller + ':5000/v3/users/' + user_id, \
                                          ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant)], \
                                          '204', 'DELETE')
        if not result:
            return False

        return True


    def list_users(self):

        result = curl.curl(self.controller + ':5000/v3/users', \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant)], \
                              '200', 'GET')
        if not result :
            return False
        users = result["users"]
        #print "all of Users: ", users  #TEST
        return users


    def __list_roles(self):

        result = curl.curl(self.controller + ':5000/v3/roles', \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant)], \
                              '200', 'GET')
        if not result :
            return False
        roles = result["roles"]
        for role in roles :
            if role["name"] == "admin" : 
                self.admin_role_id = role["id"]
            if role["name"] == "_member_" : 
                self.member_role_id = role["id"]

        return roles



    def add_tenant(self, name, desc, ram, vcpu, instances):

        request = {"project": {"description": desc , "enabled": True , "name": name, "domain_id" : "default" }}
        result = curl.curl(self.controller + ':5000/v3/projects', \
                                      ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant) ,\
                                       'Content-Type: application/json', 'Accept: application/json'], \
                                      '201', 'POST', request)
        if not result :
            return False
        print "this tenant is added: "; print result; print; print #TEST

        current_tenant_id = result['project']['id']
        print "CURRENt TENAT ID IS: " , current_tenant_id #TEST

        tenants = self. __tenants_list()
        if not tenants :
            return False
        admin_tenant_id = "" 
        for tenant in tenants :
            if  tenant['name'] == "admin" :
                        admin_tenant_id = tenant['id']
        print "ADMIN TENANT ID IS: " , admin_tenant_id;  print; print#TEST
        
        request = {"quota_set": {"cores": vcpu , "instances": instances , "ram": ram }}
        result = curl.curl(self.controller + ':8774/v2/' + admin_tenant_id + '/os-quota-sets/' + current_tenant_id, \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant),'Content-Type: application/json', "Accept: application/json"], \
                                      '200', 'PUT', request)
        if not result :
            return False
        print "this quota is added: ";print result; print; print #TyEST
        
        return True


    def __tenants_list(self):

        result = curl.curl(self.controller + ':5000/v3/projects', \
                              ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), "Accept: application/json"], \
                              '200', 'GET')
        if not result :
            return False

        tenats = result["projects"]
        #print "all of tenants: ", tenats  #TEST
        return tenats


    def remove_tenant(self, project_name):

        if project_name is None :
            print "project name cant be Null"
            return False
        tenants = self. __tenants_list()
        if not tenants :
            return False
        tenant_ids = []
        for tenant in tenants :
            if project_name in tenant['name'] :
                tenant_ids.append(tenant['id'])
        if not tenant_ids :
            print "There is not such project on open stack!"
            return False
        print "Remove Projects: name = %s id = %s" % (project_name, tenant_ids) ##TEST 
        for i in  tenant_ids :
            result = ""
            result = curl.curl(self.controller + ':5000/v3/projects/' + tenant_ids.pop(), \
                                          ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant), "Accept: application/json"], \
                                          '204', 'DELETE')
            if not result:
                return False

        return True
    


    def add_image(self, appliance_spec):
    
        print "in add image func....."

        header_list = ['X-Auth-Token: ' + self.get_token(self.username,self.password,self.tenant),  'x-image-meta-disk_format: qcow2', 'x-image-meta-container_format: bare','x-image-meta-is_public: true']

        if appliance_spec['url'] == "None" or appliance_spec['name'] == "None" :
            print "Appliance Name & appliance URL can't be None!"
            return False

            
        header_list.append('x-glance-api-copy-from: ' + re.match(r'(.*).xvm2',appliance_spec['url']).group(1) + '.qcow2' )
        header_list.append('x-image-meta-name: ' + appliance_spec['name'])


        if appliance_spec["installed_size"] != "None" :
            print "installed size is: ", appliance_spec["installed_size"]
            header_list.append('x-image-meta-size: ' + appliance_spec["installed_size"])


        if appliance_spec["memory"] != "None" :
            header_list.append('x-image-meta-min_ram: ' + appliance_spec["memory"])

        if appliance_spec["storage"] != "None" :
            header_list.append('x-image-meta-min_disk: ' + appliance_spec["storage"])
 

        print "header list is: ", header_list
        result = curl.curl(self.controller + ':9292/v1/images', header_list, '201', 'POST')

        if not result :
            return False
        print "this image meta-data is added: "; print result; print; print #TEST
        image_id = result['image']['id']
        return {"image_id": image_id}
