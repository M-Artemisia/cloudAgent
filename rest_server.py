#!/usr/bin/env python

#The rest service uses web.py to create a server and it will have two URLs, 
#one for accessing all users and one for accessing individual users:
#http://localhost:8080/users
#http://localhost:8080/users/{id}
#sudo easy_install web.py


import web
import json
import ast 
#from factories import cloudFactory
from openstackRestAdaptor import *
#Read From Config File

username ="admin" 
password = "xamin"
tenant = "admin"
controller = "http://10.1.48.25"

"""
username ="admin" 
password = "admin"
tenant = "admin"
controller = "http://10.1.48.242"
"""
params = dict(); 
params["username"] = username
params["password"] = password
params["tenant"] = tenant
params["controller"] = controller

#adaptor = cloudFactory.cloudFactory.factory("openstackRest", params)
adaptor = openstackRestAdaptor(params)
urls=(
    '/', 'hello',
    '/bye', 'bye',
    '/images', 'list_images',
    '/user', 'user_manipulation',
    '/user/(.*)', 'user_manipulation',
    '/projects/(.*)', 'projects',
    
)

class list_images:        
    def GET(self):
        images = adaptor.list_images()
        return images

class user_manipulation :
    def GET(self):
        booleanResult = adaptor.add_user() 
        return booleanResult

    def POST(self):
        data = web.data()
        user_dict = dict(); user_dict = ast.literal_eval(data)
        data_dict = user_dict['user']

        if "demo" in data_dict['project']  :
            out = adaptor.add_tenant(data_dict['project'],"Demo Project for user " + data_dict['name'], 51200,1,1)
            
            if not out :
                print "Error Accured in Adding Project ....... "
                return False

        if not adaptor.add_user(data_dict['name'],data_dict['pass'],data_dict['project']) :
            print "Error Accured in Adding User ....... "
            return False

        #convert user to JSON if it is needed
        #Convert Dict to json: json.dumps()
        #Convert json to Dict: json.loads()
        return True
 

    def DELETE(self, user_name):

        if not  adaptor.remove_user(user_name):
            print "Error Accured in Removing  User ....... "
            return False
        print "user %s is deleted!" % user_name
        return True 


class projects():   
    def DELETE(self, project_name):

        if not adaptor.remove_tenant(project_name):
            print "Error Accured in Removing  Project ....... "
            return False
        print "project %s is deleted!" % project_name
        return True 


class hello:        
    def GET(self):
        name = 'World'
        return 'Hello, ' + name + '!'

class bye:        
    def POST(self):
        data = web.data()
        return 'POST: result is ' + str (type(data)) 

    def GET(self):
        name = 'World'
        return 'GET: Bye, ' + name + '!'


if __name__ == "__main__":

    app=web.application(urls, globals())
    app.run()



#curl -i -X POST -v 127.0.0.1:8000/bye  -H 'Content-Type: application/json' -H "Accept: application/json" -d '{"user":"mali";"password":"maliheAsemani"}'

#curl -i -X POST  -v 127.0.0.1:8000/user  -H 'Cotent-Type: application/json' -H "Accept: application/json" -d '{"user":{"name":"malihe","pass":"maliheasemani","project":"demo2"}}'
