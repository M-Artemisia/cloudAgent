#!/usr/bin/env python

#The rest service uses web.py to create a server and it will have two URLs, 
#one for accessing all users and one for accessing individual users:
#http://localhost:8080/users
#http://localhost:8080/users/{id}
#sudo easy_install web.py


import os,  time
import web, json, ast 
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

demmo_user_time = 10

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
        data_dict = dict(); data_dict = ast.literal_eval(data)
        user_dict = data_dict['user']

        if "demo" in user_dict['project'] :
            return self.__demo_user(user_dict)
        
        if not self.__add_project(user_dict['project'], user_dict['description'], user_dict['ram'], user_dict['vcpu'], user_dict['instances']):
            return False

        if not self.__add_user(user_dict['name'],user_dict['pass'],user_dict['project']) :
            return False

        #convert user to JSON if it is needed
        #Convert Dict to json: json.dumps()
        #Convert json to Dict: json.loads()
        return True
        
    def __demo_user(self, user):
        if not self.__add_project(user['project'], "This is a Demo Project for user " + user['name'], 51200, 1, 1) :
            return False
        if not self.__add_user(user['name'],user['pass'],user['project']) :
            return False

        newpid = os.fork()
        if newpid == 0: # Child
            print 'I am child %d and time is %s ' % (os.getpid(), demmo_user_time)
            time.sleep(demmo_user_time)
            print; print; print "Im Removing Demo User & Project....................."
            self.__remove_project(user['project'])
            self.__remove_user(user['name'])
            os._exit(0)  

        return True
        
    def __add_user(self, name, password, project ):
        if not adaptor.add_user(name, password, project) :
            print "Error Accured in Adding User ....... "
            return False
        return True

    def __add_project(self, project, description, ram, vcpu, instances):
        out = adaptor.add_tenant(project, description, ram, vcpu, instances)
        if not out :
                print "Error Accured in Adding Project ....... "
                return False
        return True


    def __remove_project(self, project_name):
        if not adaptor.remove_tenant(project_name):
            print "Error Accured in Removing  Project ....... "
            return False
        print "project %s is deleted!" % project_name
        return True 


    def __remove_user(self, user_name):
        if not  adaptor.remove_user(user_name):
            print "Error Accured in Removing  User ....... "
            return False
        print "user %s is deleted!" % user_name
        return True 


    def DELETE(self, user_name):
        if not self. __remove_user(user_name): 
            return False
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
