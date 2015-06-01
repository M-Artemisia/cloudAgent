import os, sys, time, atexit, re
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
        #atexit.register(self.cleanup)
        self.adaptor = cloudFactory.cloudFactory.factory("openstackRest", {\
                                                    "username" : config.username,\
                                                    "password": config.password, \
                                                    "tenant": config.tenant, \
                                                    "controller": config.controller})
        self.Default_Image_User = config.Default_Image_User
        self.Default_Image_Pass = config.Default_Image_Pass
        self.Default_Linux_Image = config.Default_Linux_Image
        self.Default_Windows_Image = config.Default_Windows_Image

        self.VPC_external_network = config.VPC_external_network
        self.VPC_flavor_name = config.VPC_flavor_name
        self.VPC_sec_group = config.VPC_sec_group
        self.VPC_int_net_From = config.VPC_internal_network_From
        self.VPC_int_net_To = config.VPC_internal_network_To
        self.VPC_int_net_Range = config.VPC_internal_network_Range        
        #self.VPC_int_3rd_oct_crnt =  int(re.split('(.*)\.(.*)\.(.*)\.(.*)', self.VPC_int_net_From)[3:4].pop())

        self.VPS_project_name = config.VPS_project_name
        self.VPS_project_user = config.VPS_project_user
        self.VPS_project_pass = config.VPS_project_pass
        self.VPS_ValidIP_3oct = config.VPS_ValidIP_3oct  #RETURN VALUES SHOULD BE CAPTURED HERE OR PASSED TO THE FUNCTIONS(As a temporary solution)
        self.VPS_external_network = config.VPS_external_network
        self.VPS_internal_network = config.VPS_internal_network
        self.VPS_sec_group = config.VPS_sec_group
        

        print self._get_internal_net_add()  #Needs error handling
        

    def create_user(self,user_dict,server_dict):
        '''
        This method creates a Project and a user on Xamin Cloud. 
        @type user_dict: Dict 
        @param user_dict: It has three keys which contains user info. 
        The keys are 'name': user name; 'pass': The user password for entering to Xamin IAAS; 'project': The name of Project which has been assigned to the user
        @rtype: A dictionary #Boolean
        @return: {"status": "error"/"success" , "message":"error_message"/"returnValue"}. 
	if status is "success", message may show the value.  
	if status is "error", message contains the error message.  
        '''

        print "Creating Project....."
        if "demo" in user_dict['project'] :
            prj_desc="This is a %s project for user %s " %("Demo",user_dict['name'])
            #ram=512;cpu=1;instance_num=1
            ram=2048;cpu=1;instance_num=1
        else:
            prj_desc="This is a %s project for user %s " %("Paid",user_dict['name'])
            ram=10240;cpu=100;instance_num=40

        user_dict['project'] = user_dict['project']+ time.strftime("%Y%m%d_%H%M%S", time.gmtime()) #+'_VPC' 
        self.user = user_dict

        result = self._add_project(user_dict['project'], prj_desc, ram, cpu, instance_num)
        if result['status'] == "error" :
	    return result

        print "Creating user...."
        result = self._add_user(user_dict)
	if result['status'] == "error" :
	    #print "Cannot create user. removing tenant..."
            result = self.adaptor.remove_tenant(user_dict['project'])
            if result['status'] == "error" :
		#print "Cannot remove tenant"
		result['message'] = "Cannot create user. Removing tenant... Filed\n"+ str(result['message'])
	    else:
		result['message'] = "Cannot create user. Removing tenant... Done\n"+ str(result['message'])
            return result

        if "demo" in user_dict['project'] :
            newpid = os.fork()
            if newpid == 0: # Child
                print 'Time for Deletion is %s ' % config.demo_user_time
                time.sleep(config.demo_user_time)
                print; print "Im Removing Demo User & Project....................."
                result = self.cleanup(user_dict,server_dict) #cleanup handles error messages
                os._exit(0)  
                
        return result

    def create_VPC(self, user_dict, image):
        '''
        @rtype: A dictionary
        @return: {"status":"success", "message":"IP"} in case of success
        and {"status":"error", "message":"error message"} in case of failure
        '''

        print "CREATING Network FOR VPC....."
        #self.adaptor.add_network(user_dict['name'], user_dict['pass'], user_dict['project'] ,False ,'xaas_int4','xaas_subnet')

        print "Creating VPC.........."
        if "linux" in image :
            image = self.Default_Linux_Image
        else:
            image = self.Default_Windows_Image
        
        network_address = self._get_internal_net_add()

        int_net = 'xaas_vpc_int_'+ time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        int_subnet = 'xaas_vpc_subnet_'+ time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        router = 'xaas_vpc_router_'+time.strftime("%Y%m%d_%H%M%S", time.gmtime())

        server_name = 'Demo'
        server={'net':int_net, 'subnet':int_subnet, 'router': router, 'server': server_name}

        result = self.create_user(user_dict,server)
	if result['status'] == "error":
            return result

        print "Creating Network for VPC....."
        result = self.adaptor.add_network(user_dict['name'], user_dict['pass'], user_dict['project'], False, int_net, int_subnet, network_address)
 	if result['status'] == "error":
            print "Error in Adding Network"
            result2 = self.cleanup(user_dict,server) #cleanup handles error message
	    result['message'] = "Error in Adding Network: " + str(result['message']) +"\n"+ str(result2['message'])
	    return result

        print "Creating Router FOR VPC....."
        result = self.adaptor.add_router(user_dict['name'], user_dict['pass'], user_dict['project'], router, self.VPC_external_network, int_subnet)
	if result['status'] == "error" :
            print "Cant add router...."
            result2 = self.cleanup(user_dict,server)
	    result['message'] = "Error in Adding Router: " + str(result['message']) +"\n"+ str(result2['message'])
            return result

        print "Creating a demo VPS on VPC .........."
        print "flavor in config file is: ", self.VPC_flavor_name 
        result = self.adaptor.install_server(user_dict['name'], user_dict['pass'], user_dict['project'] , server_name, self.VPC_external_network, int_net, self.Default_Image_User, self.Default_Image_Pass, self.VPC_sec_group, image, self.VPC_flavor_name)
        if result['status'] == "error" :
            print "Cant create instance.."
            self.cleanup(user_dict,server)
	    result['message'] = "Error in install_server: Cannot create instance. " + str(result['message']) +"\n"+ str(result2['message'])
            return result
    	else:
	    ip = result['message']
	    print "Valid_ip in cloud wrapper is: ", ip 
        return result

    def create_VPS(self, image, ram, vcpus, disk):

        if "linux" in image :
            image = self.Default_Linux_Image
        else:
            image = self.Default_Windows_Image

        flavor = "xaas_flavor_"+time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        result = self.adaptor.add_flavor(self.VPS_project_user, self.VPS_project_pass, self.VPS_project_name, flavor, ram, vcpus, disk)
	if result['status'] == "error":
	    result['message'] = "Failed to add flavor:\n"+ str(result['message'])  #because computeWrapper does not return complete messages
            return result


        print "Creating a demo VPS .........."
        server = "VPS_"+time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        
        ip_result = self.adaptor.install_server(self.VPS_project_user, self.VPS_project_pass, self.VPS_project_name , server, self.VPS_external_network, self.VPS_internal_network, self.Default_Image_User, self.Default_Image_Pass, self.VPS_sec_group , image, flavor)
        if ip_result['status'] == "error":
            print "Cant create instance.."
            result2 = self.adaptor.remove_flavor(self.VPS_project_user, self.VPS_project_pass, self.VPS_project_name, flavor)
            ip_result['message'] = "Error in install_server: Cannot create instance" + str(ip_result['message']) +"\n"+ str(result2['message'])
	    return ip_result
	#ip = result['message']

        print "I am removing flavor..............."
        result = self.adaptor.remove_flavor(self.VPS_project_user, self.VPS_project_pass, self.VPS_project_name, flavor)
	if result['status'] == "error":
	    print "Failed to remove Flavor" #only print. don't return becuase the server has installed.
        	
	return ip_result #contains ip


    def create_Image(self, image_info_dic):

        #result = self.adaptor.add_image(self.VPS_project_user, self.VPS_project_pass, self.VPS_project_name, flavor, ram, vcpus, disk)
        result = self.adaptor.add_image(image_info_dic)
	#if result['status'] == "error":
	    
        #    return result
        return result



    #*************************************PRIVATE FUNCTIONS**************************
    def _add_user(self, user_dict):
        result = self.adaptor.add_user(user_dict['name'], user_dict['pass'], user_dict['project'])
	if result['status'] == "error" :
            #print "Error Accured in Adding User ....... "
	    result['message'] = "Error Accured in Adding User ....... \n" + result['message']
            return result
        return result

    def _add_project(self, project_name, description, ram, vcpu, instances):
        result = self.adaptor.add_tenant(project_name, description, ram, vcpu, instances)
        if result['status'] == "error" :
            #print "Error Accured in Adding Project ....... "
            result['message'] = "Error Accured in Adding Project ....... \n" + result['message']
            return result
        return result

    def _get_internal_net_add(self):

        #file = open("/root/asemani/new_xaas_2/apps/xCloudAgent/test.ini", "r")
        file = open("test.ini", "r")
        print os.getcwd() 
        self.VPC_int_3rd_oct_crnt = file.read()
        file.close()
        print "first line in function: _3rd_crnt is: ", self.VPC_int_3rd_oct_crnt

        octets = re.split('(.*)\.(.*)\.(.*)\.(.*)', self.VPC_int_net_From)
        first_octet = octets[1:2].pop()
        second_octet = octets[2:3].pop() 
        third_octet = octets[3:4].pop() 
	print "third_octet is ",third_octet
        
        if int(self.VPC_int_3rd_oct_crnt) < int(third_octet) :
            self.VPC_int_3rd_oct_crnt = int(third_octet)
        else :
            self.VPC_int_3rd_oct_crnt = int(self.VPC_int_3rd_oct_crnt) + 1
            if int(self.VPC_int_3rd_oct_crnt) >= int(re.split('(.*)\.(.*)\.(.*)\.(.*)', self.VPC_int_net_To)[3:4].pop()) :
                self.VPC_int_3rd_oct_crnt = int(third_octet)
        
        network_address = first_octet + '.' + second_octet + '.' + str(self.VPC_int_3rd_oct_crnt) + '.0/' + self.VPC_int_net_Range
        print; print "step2"
        file = open("test.ini", "w")
        file.write("%s" % self.VPC_int_3rd_oct_crnt)
        file.close()

        print; print "step3"
        file = open("test.ini", "r")
        print file.read()
        file.close()

        return network_address

    def cleanup(self,user, server = None):
	'''
	@rtype: A dictionary #Boolean
        @return: {"status":"success", "message":"NotImportant"} in case of success
	and {"status":"error", "message":"error message"} in case of failure
        '''


        print "Cleaning Environment...."

        if bool(server) :
            print "cleaning Server "

            print; print; print "Removing Server ********************************************* ", server[ 'server']
            result = self.adaptor.remove_server(user['name'], user['pass'], user['project'], server[ 'server'])
	    if result['status'] == "success":
                time.sleep(3.0)
                print; print; print "Removing Router ********************************************* ", server['router']
                #if self.adaptor.remove_router(user['name'], user['pass'], user['project'], server['router'], server['subnet']) :
                result = self.adaptor.remove_router(user['name'], user['pass'], user['project'], server['router'], server['subnet'])
		if result['status'] == "success":
                    print; print; print "Removing Network ********************************************* ", server['net']
                    result2 = self.adaptor.remove_network(user['name'], user['pass'], user['project'], server['net'], server['subnet'])
                    if result2['status'] == "error":
			result2['message'] = "Cleaning Server: Failed to remove network :\n"+ str(result2['message'])
			return result2
		else:
		    result['message'] = "Cleaning Server: Failed to remove router :\n"+ str(result['message'])
		    return result
		    
            else:
		result['message'] = "Cleaning Server: Failed to remove server :\n" + result['message'] #temp - until couldWrapper or  does it
                return result

            ''' 
            if self.adaptor.remove_router(user['name'], user['pass'], user['project'], server['router'], server['subnet']) :

                print "Removing Network will be implemented in the next version..."
                if not self.adaptor.remove_network(user['name'], user['pass'], user['project'], server['net'], server['subnet']):
                return False
            else:
                return False
            '''

        if bool(user) :
            print; print; print "cleaning user *********************************************  ", user['project'], user['name']
            result = self.adaptor.remove_tenant(user['project'])
	    if result['status'] == "error" :
		result['message'] = "Cleaning User: Failed to remove tenant so does the user :\n"+ str(result['message'])
	    	return result
	    
            result2 = self.adaptor.remove_user(user['name'])
	    if result2['status'] == "error" :
                result2['message'] = "Cleaning User: Failed to remove user :\n"+ str(result2['message'])
                return result2


        return result
