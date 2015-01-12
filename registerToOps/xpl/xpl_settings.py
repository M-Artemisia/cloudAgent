#!/usr/bin/python
#GLOBAL CONFIGURATION FOR RMS CODE IN JNEKINS
#Author: aLaa rahimi
#Date: June 1.2014

#CDN HOST public URL for cdn host
#Example: "http://10.1.48.221/mnt/nfs/devel/appliances/"
CDN_HOST = "http://10.1.48.219/devel/appliances/"
nbd_db="/mnt/nfs/jenkins/xaminScripts/rms/nbd.db"

#JENKINS CONFIGURATIONS
# used in :rms_deamon.py 
#Jenkins job path
jenkinsHome="/var/lib/jenkins/jobs/"
#The location of rms code in jenkins 
rmsStaticLocation="/var/lib/jenkins/rms/"

#TEMP DIRECTORY OF IMAGES
# used in: disk.py & xmimage.py
disk_tmp_directory = '/var/lib/rms/images/'
disk_image_directory_prefix='xmbuilder-'
disk_image_name_suffix='.xaminappl'
# used in: bootstrap.py
general_skeleton_directory="/var/lib/rms/general/"


# WEB SERVER IMAGE URL
# This path will be registered to peace as the download url of the appliance
# used in : disk.py
WEB_SERVER_PREFIX = "/mnt/nfs/devel/appliances/"



#XAMIN CLOUD AGENT
xaminCloudAgentUrl  = '10.1.48.25'
xaminCloudAgentPort = '8000'
