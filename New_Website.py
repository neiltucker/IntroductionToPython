# Create a Resource Group and Storage Account in Microsoft Azure
# Resource Groups are used to store and organize resources in Azure.
# Storage Accounts are used to store & share your data & files in different formats.
# Run this code from a python session on the Azure Cloud Shell.
# After the resource group and storage account are created, verify their existence from the Azure Portal (http://portal.azure.com)

### Install modules needed to create Azure VM from PowerShell or Bash console
'''
# importlib package must be installed for this script to work
# pip install importlib
# If modules become unstable during exercises, uninstall and then reinstall them.  
# You may also need to rename or move all files in the azure configuration folder /home/<USER>/.azure
# pip uninstall azure azure.cli azure.cli.core azure.mgmt azure.common azure.storage azure.storage.common azure.storage.blob azure.storage.file
pip install --user azure azure.cli azure.cli.core azure.mgmt azure.common azure.storage azure.storage.common azure.storage.blob azure.storage.file
pip list
python
'''

### This looping operation will install the modules not already configured.
import importlib, os, sys, datetime
packages = ['azure', 'azure.cli', 'azure.cli.core', 'azure.mgmt', 'azure.mgmt.storage', 'azure.common', 'azure.storage',  'azure.storage.common', 'azure.storage.blob', 'azure.storage.file']
for package in packages:
  try:
    module = importlib.__import__(package)
    print(package, ' package was imported.')
    globals()[package] = module
  except ImportError:
    cmd = 'pip install --user ' + package
    print('Please wait.  Package is being installed: ', package)
    os.system(cmd)
    module = importlib.__import__(package)
    print(package, ' package was imported.')


# These modules are used for authenticating to Azure, using resources and managing storage.  
# Install them if they are not already on the system: pip install --upgrade --user azure-common azure-mgmt azure-storage
import datetime, os, ftplib, xml.etree.ElementTree as ET
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.common import CloudStorageAccount
from azure.storage.file import FileService
from azure.storage.blob import PublicAccess
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import AppServicePlan, SkuDescription, Site, SiteAuthSettings
# Configure Clients for Managing Resources
resource_client = get_client_from_cli_profile(ResourceManagementClient)
storage_client = get_client_from_cli_profile(StorageManagementClient)
web_client = get_client_from_cli_profile(WebSiteManagementClient)
# Configure Variables
nameprefix = 'np' + (datetime.datetime.now()).strftime('%H%M%S')
resourcegroupname = nameprefix + 'rg'
storageaccountname = nameprefix + 'sa'
serverfarmname = nameprefix + 'sf'
websitename = nameprefix + 'web'
location = 'eastus'
sharename = nameprefix + 'share'
profilefilename = websitename+'.xml'
# create a test file to be uploaded to your blob and file share
os.system('echo "<h1> This is my first Azure web-site. </h1>" > index.html')
os.system('echo "<br />" >> index.html')
os.system('echo "<h1> And yes, Python is better than chocolate. </h1>" >> index.html')
os.system('echo "<br /> <br />" >> index.html')
os.system('echo "<h1><a href = "hostingstart.html"> Template Page </a></h1>" >> index.html')
filename = 'index.html'

def main():
    # Create the Resource Group and Storage Account.  Use Azure Portal to examine their properties before deleting them.
    resource_group_params = {'location':location}
    global resource_group, storage_account
    resource_group = resource_client.resource_groups.create_or_update(resourcegroupname, resource_group_params)
    storage_account = storage_client.storage_accounts.create(resourcegroupname, storageaccountname, {'location':location,'kind':'storage','sku':{'name':'standard_ragrs'}})
    storage_account.wait()


main()

def shares():
    # Create Container and Share
    global storage_account_key, blob_service, blob_share, file_service, file_share
    sak = storage_client.storage_accounts.list_keys(resourcegroupname, storageaccountname)
    storage_account_key = sak.keys[0].value
    cloudstorage_client =  CloudStorageAccount(storageaccountname,storage_account_key)
    blob_service = cloudstorage_client.create_block_blob_service()
    blob_share = blob_service.create_container(sharename,public_access=PublicAccess.Container)
    file_service = FileService(account_name=storageaccountname, account_key=storage_account_key)
    file_share = file_service.create_share(sharename)
    # Copy Setup Files to Container and Share
    blob_service.create_blob_from_path(sharename,filename,filename,)
    file_service.create_file_from_path(sharename,'',filename,filename,)


shares()


def app_service_plan():
    # The next two lines will create errors.  Research pdb if uncertain how to proceed (e.g. help(pdb)
    # If you wish to proceed with troubleshooting, comment out the next two lines.
    # import pdb
    # pdb.set_trace()
    # Create an App Service Plan
    global service_plan
    # RESOURCEGROUPNAME variable has not been defined.  Uncomment the line below to fix this error.
    RESOURCEGROUPNAME = resourcegroupname
    service_plan_async_operation = web_client.app_service_plans.create_or_update(
        RESOURCEGROUPNAME,
        serverfarmname,
        AppServicePlan(
            app_service_plan_name=serverfarmname,location=location,
            sku=SkuDescription(
                name='F1',capacity=10,tier='Free'
            )
        )
    )
    service_plan = service_plan_async_operation.result()


app_service_plan()

def app_web_site():
    # Create Web-Site
    global website
    site_async_operation = web_client.web_apps.create_or_update(
        resourcegroupname,
        websitename,
        Site(
            location=location,
            server_farm_id=service_plan.id
        )
    )
    website = site_async_operation.result()
    if website.state == 'Running': print("Website http://" +  website.default_host_name + " has deployed successfully.")
    else: print("Website not deployed successfully.")

    
app_web_site()

def ftp_upload():
    # View the new web-site before proceeding with the following steps. 
    # Get Profile Information to Extract FTP Credentials
    global username, password, ftpserver
    profile_list = list(web_client.web_apps.list_publishing_profile_xml_with_secrets(resourcegroupname,websitename))
    publishsettingsfile = open(profilefilename,'w+')
    for n in profile_list: 
        publishsettingsfile.write(str(n))
    publishsettingsfile.close()
    xml = ET.fromstring(profile_list[0])
    for table in xml.iter('publishData'):
        for record in table:
            print(record.tag, record.text)
    # Upload Files To Web-Site Using FTP
    username = websitename
    password = record.get('userPWD')
    ftpserver = (record.get('publishUrl')).replace('ftp://w','w')
    ftpserver = (ftpserver).replace('net/site/wwwroot','net')
    ftp = ftplib.FTP(ftpserver)
    ftp.connect()
    ftp.login(username,password)
    ftp.cwd('/site/wwwroot')
    ftp.storbinary('STOR '+filename, open(filename,'rb'))
    ftp.quit()

    
ftp_upload()

# Delete Resource Group.  Deleting a resource group will also deleted all objects in it.
# delete_async_operation = resource_client.resource_groups.delete(resourcegroupname)
# delete_async_operation.wait()


