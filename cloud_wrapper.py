import os, sys, time


app_path = os.path.dirname(__file__)
sys.path.append(app_path)

if app_path:
    os.chdir(app_path)
else:
    app_path = os.getcwd()


from factories import cloudFactory
import config

class xass_wrapper:

    def __init__(self):
        self.adaptor = cloudFactory.cloudFactory.factory("openstackRest", {\
                                                    "username" : config.username,\
                                                    "password": config.password, \
                                                    "tenant": config.tenant, \
                                                    "controller": config.controller})
    def create_user(self,user_dict):
        
        if "demo" in user_dict['project'] :
            prj_desc="This is a %s project for user %s " %("Demo",user_dict['name'])
            ram=51200;cpu=1;instance_num=1
            user_dict['project'] = user_dict['project'] + time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        else:
            prj_desc="This is a %s project for user %s " %("Real",user_dict['name'])
            ram=102400;cpu=1;instance_num=1


        if not self._add_project(user_dict['project'], prj_desc, ram, cpu, instance_num) :
            return False
        if not self._add_user(user_dict) :
            return False

        if "demo" in user_dict['project'] :
            newpid = os.fork()
            if newpid == 0: # Child
                print 'Time for Deletion is %s ' % config.demo_user_time
                time.sleep(config.demo_user_time)
                print; print "Im Removing Demo User & Project....................."
                self._remove_project(user_dict['project'])
                self._remove_user(user_dict['name'])
                os._exit(0)  
                
        return True

    def create_vpc(self, user_dict): #Virtual Private Cloud
        print "CREATING USER FOR VPC....."
        #self.create_user(user_dict)

        print "CREATING Network FOR VPC....."
        #self.adaptor.add_network(user_dict['name'], user_dict['pass'], user_dict['project'] ,False ,'xaas_int4','xaas_subnet')

        print "CREATING Router FOR VPC....."
        #self.adaptor.add_router(user_dict['name'], user_dict['pass'], user_dict['project'], 'xaas_router1','ext-net','xaas_subnet')

        self.adaptor.install_image(user_dict['name'], user_dict['pass'], user_dict['project'] , "demo", 'ext-net', 'xaas_int4')
    
        return True

    #*************************************PRIVATE FUNCTIONS**************************
    def _add_user(self, user_dict):
        if not self.adaptor.add_user(user_dict['name'], user_dict['pass'], user_dict['project']) :
            print "Error Accured in Adding User ....... "
            return False

        print "Adding role...."
        self.adaptor.add_user_role(user_dict['name'], user_dict['project'])
        return True

    def _add_project(self, project_name, description, ram, vcpu, instances):
        out = self.adaptor.add_tenant(project_name, description, ram, vcpu, instances)
        if not out :
            print "Error Accured in Adding Project ....... "
            return False
        return True


    def _remove_project(self, project_name):
        if not self.adaptor.remove_tenant(project_name):
            print "Error Accured in Removing  Project ....... "
            return False
        print "project %s is deleted!" % project_name
        return True 


    def _remove_user(self, user_name):
        if not  self.adaptor.remove_user(user_name):
            print "Error Accured in Removing  User ....... "
            return False
        print "user %s is deleted!" % user_name
        return True 


user="asemani"
password= "123"
prj="VPC_XAAS"

wrapper = xass_wrapper()
wrapper.create_vpc({"name":user, "pass": password, "project": prj})
