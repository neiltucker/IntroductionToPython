### Create a virtual environment before using the python shell.
### Use a Bash shell to run the commands in the next section before running the python commands

'''
### If using a virtualized environment (virtualenv or venv)
# pip install --upgrade virtualenv or pip install --upgrade venv
# cd ~
# mkdir pyenv
# virtualenv -p python3 pyenv or python3 -m venv pyenv
# cd pyenv
# source bin/activate  
'''

### Install modules needed to create Azure VM from PowerShell or Bash console
'''
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


from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.common import CloudStorageAccount
from azure.storage.blob import PublicAccess
from azure.storage.file import FileService
from azure.mgmt.network import NetworkManagementClient
homedirectory = os.path.expanduser("~")
workfolder = os.path.normpath(homedirectory + '/clouddrive/labfiles.55264a/')
os.chdir(homedirectory)
nameprefix = 'in' + (datetime.datetime.now()).strftime('%H%M%S')
resourcegroupname = nameprefix + 'rg'
storageaccountname = nameprefix + 'sa'
publicipname1 = nameprefix + 'publicip1'
virtualnetworkname = nameprefix + 'vn'
subnetname1 = nameprefix + 'sub1'
nicname1 = nameprefix + 'nic1'
containername = '55264a'
foldername = 'labfiles.55264a'
configfilename = '55264customscriptextension.ps1'
zipfilename = '55264A-ENU_SetupFiles.zip'
fileuri = 'https://' + storageaccountname + '.blob.core.windows.net/' + containername + '/' + configfilename
location = 'eastus'
vmname = 'vm55264srv'
adminuser = 'adminz'
password = 'Pa$$w0rdPa$$w0rd'

# Configure Client Services
resource_client = get_client_from_cli_profile(ResourceManagementClient)
storage_client = get_client_from_cli_profile(StorageManagementClient)
network_client = get_client_from_cli_profile(NetworkManagementClient)
compute_client = get_client_from_cli_profile(ComputeManagementClient)

# Create Resource Group & Storage Account
resource_group_params = {'location':location}
resource_client.resource_groups.create_or_update(resourcegroupname, resource_group_params)
storageaccount = storage_client.storage_accounts.create(resourcegroupname, storageaccountname, {'location':location,'kind':'storage','sku':{'name':'standard_ragrs'}})
storageaccount.wait()

# Create Container and Share
os.chdir(workfolder)
sak = storage_client.storage_accounts.list_keys(resourcegroupname, storageaccountname)
storageaccountkey = sak.keys[0].value
cloudstorage_client =  CloudStorageAccount(storageaccountname,storageaccountkey)
blob_service = cloudstorage_client.create_block_blob_service()
blob_service.create_container(containername,public_access=PublicAccess.Container)
file_service = FileService(account_name=storageaccountname, account_key=storageaccountkey)
file_service.create_share(containername)

# Create The PowerShell Script Extension File used to Customize the VM
os.chdir(workfolder)
csefile = open('55264cse.tmp', 'w')
csefile.write('### Copy From Blob Using Mapped Network Drive\n')
csefile.write('$WorkFolder = "c:\labfiles.55264a\\" ; $FileShareName = "55264a"\n')
csefile.write('New-Item -Path $WorkFolder -Type Directory -Force\n')
csefile.write('$StorageAccountName = "' + storageaccountname + '"\n')
csefile.write('$StorageAccountKey = "' + storageaccountkey + '"\n')
csefile.close()
os.system('cat 55264cse.tmp 55264customscriptextension.tmp > 55264customscriptextension.ps1')

# Copy Setup Files to Container and Share
blob_service.create_blob_from_path(containername,configfilename,configfilename,)
blob_service.create_blob_from_path(containername,zipfilename,zipfilename,)
file_service.create_file_from_path(containername,'',configfilename,configfilename,)
file_service.create_file_from_path(containername,'',zipfilename,zipfilename,)

# Create Public IP Address
def create_public_ip_address(network_client):
    public_ip_addess_params = {
        'location': location,
        'public_ip_allocation_method': 'Dynamic'
    }
    public_ip_address_result = network_client.public_ip_addresses.create_or_update(
        resourcegroupname,
        publicipname1,
        public_ip_addess_params
    )
    return public_ip_address_result.result()

public_ip_address = create_public_ip_address(network_client)

# Create Virtual Network
def create_vnet(network_client):
    vnet_params = {
        'location': location,
        'address_space': {
            'address_prefixes': ['10.1.0.0/16']
        }
    }
    vnet_result = network_client.virtual_networks.create_or_update(
        resourcegroupname,
        virtualnetworkname,
        vnet_params
    )
    return vnet_result.result()

vnet = create_vnet(network_client)

# Create Subnet
def create_subnet(network_client):
    subnet_params = {
        'address_prefix': '10.1.0.0/24'
    }
    subnet_result = network_client.subnets.create_or_update(
        resourcegroupname,
        virtualnetworkname,
        subnetname1,
        subnet_params
    )
    return subnet_result.result()

subnet = create_subnet(network_client)

# Create Network Interface
def create_nic(network_client):
    subnet_info = network_client.subnets.get(
        resourcegroupname, virtualnetworkname, subnetname1
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        resourcegroupname, publicipname1
    )
    nic_params = {
        'location': location,
        'ip_configurations': [{
            'name': 'myIPConfig',
            'public_ip_address': publicIPAddress,
            'subnet': {
                'id': subnet_info.id
            }
        }]
    }
    nic_result = network_client.network_interfaces.create_or_update(
        resourcegroupname, nicname1, nic_params
    )
    return nic_result.result()

nic = create_nic(network_client)

# Create VM
def create_vm(network_client, compute_client):  
    nic = network_client.network_interfaces.get(
        resourcegroupname, nicname1
    )
    vm_parameters = {
        'location': location,
        'os_profile': {
            'computer_name': vmname,
            'admin_username': adminuser,
            'admin_password': password
        },
        'hardware_profile': {
            'vm_size': 'Standard_D11'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': 'MicrosoftSQLServer',
                'offer': 'SQL2017-WS2016',
                'sku': 'SQLDEV',
                'version': 'latest'
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic.id
            }]
        },
    }
    vm_result = compute_client.virtual_machines.create_or_update(
        resourcegroupname, 
        vmname, 
        vm_parameters
    )
    return vm_result.result()

vm = create_vm(network_client, compute_client)

## Using CustomScriptExtension to run configuration script on VM
script_parameters = {
    'location': location,
    'publisher': 'Microsoft.Compute',
    'virtual_machine_extension_type': 'CustomScriptExtension',
    'type_handler_version': '1.9',
    'auto_upgrade_minor_version': True,
    'settings': {
        'fileUris': [fileuri],
        'commandToExecute': "powershell.exe -NoProfile -ExecutionPolicy Bypass -File 55264customscriptextension.ps1"
    }, 
    'protected_settings' : {'storageAccountName': storageaccountname,'storageAccountKey': storageaccountkey},
}
vm_script = compute_client.virtual_machine_extensions.create_or_update(
    resourcegroupname, vmname, 'CustomScriptExtension', script_parameters
)

vm_script.wait()
vm_script.status()

### Note: Azure VMs incure cost even if they are not being used or the operating system is shutdown.
### Note: The VM must be powered down to deallocate is resources and eliminate the usage charges.
# Shutdown, Start or Restart VM
# compute_client.virtual_machines.power_off(resourcegroupname,vmname)
# compute_client.virtual_machines.start(resourcegroupname,vmname)
# compute_client.virtual_machines.restart(resourcegroupname,vmname)

### Deleting the Resource Group automatically deletes all the resources in it, including the VM
# delete_async_operation = resource_client.resource_groups.delete(resourcegroupname)
# delete_async_operation.wait()



