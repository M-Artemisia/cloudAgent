import os, sys, time, atexit

'''
app_path = os.path.dirname(__file__)
sys.path.append(app_path)

if app_path:
    os.chdir(app_path)
else:
    app_path = os.getcwd()
'''

from factories import cloudFactory
import config

class xass_wrapper:

    def __init__(self):
        self.user = {}
        self.server={}
        #signal.signal(signal.SIGINT, self.signal_handler())
#        atexit.register(self.cleanup)
        self.adaptor = cloudFactory.cloudFactory.factory("openstackRest", {\
                                                    "username" : config.username,\
                                                    "password": config.password, \
                                                    "tenant": config.tenant, \
                                                    "controller": config.controller})
    def create_user(self,user_dict):
        '''
        This method creates a Project and a user on Xamin Cloud. 
        @type user_dict: Dict 
        @param user_dict: It has three keys which contains user info. 
        The keys are 'name': user name; 'pass': The user password for entering to Xamin IAAS; 'project': The name of Project which has been assigned to the user
        @rtype: Boolean
        @return: False if there is any problem in adding user or project, otherwise True will be returned. 
        '''

        print "Creating Project....."
        if "demo" in user_dict['project'] :
            prj_desc="This is a %s project for user %s " %("Demo",user_dict['name'])
            ram=512;cpu=1;instance_num=1
        else:
            prj_desc="This is a %s project for user %s " %("Paid",user_dict['name'])
            ram=1024;cpu=1;instance_num=1

        user_dict['project'] = user_dict['project'] + time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        self.user = user_dict

        if not self._add_project(user_dict['project'], prj_desc, ram, cpu, instance_num) :
            self.cleanup(user_dict)
            return False

        print "Creating user...."
        if not self._add_user(user_dict) :
            self.cleanup(user_dict)
            return False

        if "demo" in user_dict['project'] :
            newpid = os.fork()
            if newpid == 0: # Child
                print 'Time for Deletion is %s ' % config.demo_user_time
                time.sleep(config.demo_user_time)
                print; print "Im Removing Demo User & Project....................."
                #self.cleanup(user_dict)
                self._remove_project(user_dict['project'])
                self._remove_user(user_dict['name'])
                os._exit(0)  
                
        return True

    def create_vpc(self, user_dict, image, ip_range):

        '''
        This method creates a Virtual Private Cloud for a user, and run a demo instance for it.
        @type user_dict: Dict 
        @param user_dict: It has three keys which contains user info. 
        The keys are 'name': user name; 'pass': The user password for entering to Xamin IAAS; 'project': The name of Project which has been assigned to the user
        @type image: String 
        @param image: The type of the image of the server. It can be 'linux' or 'windows' 
        @type ip_range: String 
        @param ip_range: this is a String which show network Address of the internal network of the project. Example: '192.168.10.0/24'
        @rtype: Boolean
        @return: False if there is any problem in creating the VPC, otherwise True will be returned. 
        '''

        print "Creating VPC.........."
        
        if not self.create_user(user_dict):
            return False
        
        if "linux" in image :
            image = 'cirros-2'
        else:
            image =  'windows'
        
        ext_net='ext'

        network_address = ip_range        
        int_net = 'xaas_int'+ time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        int_subnet = 'xaas_subnet'+ time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        router = 'xaas_router'+time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        server_name = 'Demo'
        self.server={'int_net':int_net, 'subnet':int_subnet, 'router': router, 'server': server_name}

        print "Creating Network for VPC....."
        if not self.adaptor.add_network(user_dict['name'], user_dict['pass'], user_dict['project'], False, int_net, int_subnet, network_address):
            print "Error in Adding Network"
            self.cleanup(user_dict)
            return False

        print "Creating Router FOR VPC....."
        if not self.adaptor.add_router(user_dict['name'], user_dict['pass'], user_dict['project'], router, ext_net, int_subnet):
            print "Cant add router...."
            self.cleanup(user_dict)
            return False

        if "demo" in user_dict['project'] :
            print "Creating a demo VPS on demo VPC .........."
            if not self.adaptor.install_server(user_dict['name'], user_dict['pass'], user_dict['project'] , server_name, ext_net, int_net, 'default', image, 'm1.tiny'):
                print "Cant create instance.."
                self.cleanup(user_dict)
                return False
            return True

        print "Creating a demo VPS on VPC .........."
        if not self.adaptor.install_server(user_dict['name'], user_dict['pass'], user_dict['project'] , server_name, ext_net, int_net, 'default', image,  'm1.tiny'):
            print "Cant create instance.."
            self.cleanup(user_dict)
            return False
    
        return True


    #*************************************PRIVATE FUNCTIONS**************************
    def _add_user(self, user_dict):
        if not self.adaptor.add_user(user_dict['name'], user_dict['pass'], user_dict['project']) :
            print "Error Accured in Adding User ....... "
            return False
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

    '''
    def cleanup(self):
        print "Cleaning Environment...."
        if bool(self.user) :
            print "cleaning user......"
            self._remove_project(self.user['project'])
            self._remove_user(self.user['name'])
        if bool(self.server) :
            print "cleaning Server "
            self._remove_server(self.server[ 'server'])
            self._remove_router(self.server['router'])
            self._remove_net(self.server['int_net'])
    '''

    def cleanup(self,user):
        print "Cleaning Environment...."
        if bool(user) :
            print "cleaning user......"
            self._remove_project(user['project'])
            self._remove_user(user['name'])
        '''
        if bool(self.server) :
            print "cleaning Server "
            self._remove_server(self.server[ 'server'])
            self._remove_router(self.server['router'])
            self._remove_net(self.server['int_net'])
        '''


    def _remove_server(self, server):
        print "Removing Server will be implemented in the next version..."
        return 

    def _remove_router(self, router):
        print "Removing Router will be implemented in the next version..."
        return 

    def _remove_net(self, int_net):
        print "Removing Network will be implemented in the next version..."
        return 

