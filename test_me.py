from cloud_wrapper import xass_wrapper


user="asemani_demo_1"
password= "mali123asemani098_"
prj="VPC_XAAS_demo"

wrapper = xass_wrapper()


print wrapper.create_VPC({"name":user, "pass": password, "project": prj},'linux')


'''
int_net = 'xaas_int'+'_VPC'
int_subnet = 'xaas_subnet'+'_VPC'
router = 'xaas_router'+'_VPC'

server_name = 'Demo'
server={'net':int_net, 'subnet':int_subnet, 'router': router, 'server': server_name}
print wrapper.cleanup({"name":user, "pass": password, "project": prj+'_VPC'}, server)
'''
#create_VPS(self, image, ram-M, vcpus, disk-G)
print wrapper.create_VPS('linux', 3000, 1, 10)




#user2="asemani_demo_2"
#print wrapper.create_VPC({"name":user2, "pass": password, "project": prj},'linux')
#print wrapper.create_vpc({"name":user, "pass": password, "project": prj},'linux','192.168.83.0/24')

'''
create_user(user_dict) Function

This method creates a Project and a user on Xamin Cloud. 
@type user_dict: Dict 
@param user_dict: It has three keys which contains user info. 
The keys are 'name': user name; 'pass': The user password for entering to Xamin IAAS; 'project': The name of Project which has been assigned to the user
@rtype: Boolean
@return: False if there is any problem in adding user or project, otherwise True will be returned. 




create_vpc(user_dict, image, ip_range) Function

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
