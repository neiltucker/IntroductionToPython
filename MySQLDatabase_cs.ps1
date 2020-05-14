### Create Azure MySQL Server & Database using the Azure Cloud Shell (cs)
### Configure Objects & Variables
Set-StrictMode -Version 2.0
$SubscriptionName = (Get-AzureRMSubscription)[0].Name                                 # Replace with the name of your preferred subscription
$CloudDriveMP = (Get-CloudDrive).MountPoint
$WorkFolder = "/home/$env:USER/"
Set-Location $WorkFolder
$ExternalIP = ((Invoke-WebRequest -URI IPv4.Icanhazip.com -UseBasicParsing).Content).Trim()                                          # You may substitute with the Internet IP of your computer
If (Get-Module -ListAvailable -Name SQLServer) {Write-Output "SQLServer module already installed" ; Import-Module SQLServer} Else {Install-Module -Name SQLServer -Force ; Import-Module -Name SQLServer}
$SQLLogin1 = "sqllogin1"
$Password = 'Password1234'
$PW = Write-Output $Password | ConvertTo-SecureString -AsPlainText -Force        # Password for SQL Database server
$SQLCredentials =  (New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $SQLLogin1, $PW)
$Location = "EASTUS"
$DataLocation = "EASTUS"   				        	   # Verify that this location supports the creation of MySQL Server objects
$NamePrefix = "in" + (Get-Date -Format "HHmmss")       # Replace "in" with your initials.  Date information is added in this example to help make the names unique
$ResourceGroupName = $NamePrefix.ToLower() + "rg"
$StorageAccountName = $NamePrefix.ToLower() + "sa"     # Must be lower case
$MySQLServerName = 'ms' + $NamePrefix
$MySQLServerFQDN = $MySQLServerName + '.mysql.database.azure.com'
$DefaultDatabase= 'mysql'
$MySQLDB = 'mysqldb1'
$SQLLogin1 = "SQLLogin1"
$SQLLogin1UPN = $SQLLogin1 + "@" + $MySQLServerName
$Password = 'Password1234'
$SecurePassword = ConvertTo-SecureString -AsPlainText $Password -Force
$MySQLCredentials =  (New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $SQLLogin1UPN, $SecurePassword)
$MySQLConnectionString = "Server=$MySQLServerFQDN;Port=3306;Database=$DefaultDatabase;Uid=$SQLLogin1UPN;Pwd=$Password;SslMode=Required;"
$SAShare = "sashare"                                    # Must be lower case
$TMPData = $WorkFolder + "employees.tmp"
$SQLData = $WorkFolder + "employees.sql"
$CustomerCSV = $WorkFolder + "customer.csv"


### Log start time of script
$logFilePrefix = "AzureMySQL" + (Get-Date -Format "HHmm") ; $logFileSuffix = ".txt" ; $StartTime = Get-Date
"Create Azure Server and Database"   >  $WorkFolder$logFilePrefix$logFileSuffix
"Start Time: " + $StartTime >> $WorkFolder$logFilePrefix$logFileSuffix

### Login to Azure
# Connect-AzureRmAccount
$Subscription = Get-AzureRmSubscription -SubscriptionName $SubscriptionName | Set-AzureRMContext
Register-AzureRmResourceProvider -ProviderNamespace Microsoft.SQL

### Create Resource Group, Storage Account & Storage Account Share
New-AzureRMResourceGroup -Name $ResourceGroupName  -Location $Location
New-AzureRMStorageAccount -ResourceGroupName $ResourceGroupName -Name $StorageAccountName -Location $Location -Type Standard_RAGRS
$StorageAccountKey = (Get-AzureRmStorageAccountKey -ResourceGroupName $ResourceGroupName -Name $StorageAccountName)[0].Value
$StorageAccountContext = New-AzureStorageContext -StorageAccountName $StorageAccountName -StorageAccountKey $StorageAccountKey
$BlobContainer = New-AzureStorageContainer -Name $SAShare.ToLower() -Context $StorageAccountContext -Permission Container -Verbose
$BlobLocation = $BlobContainer.cloudblobcontainer.Uri.AbsoluteUri
Get-ChildItem -File $WorkFolder"employees.*" | Set-AzureStorageBlobContent -Container $SAShare -Context $StorageAccountContext -Force

### Create MySQL Server and Database (We will use Azure CLI for this part of the lab)
# az extension add --name rdbms          # This option is sometimes required for MySQL commands to work.  Ignore any error messages it may generate and continue.
$MySQLServerInstance = az mysql server create -n $MySQLServerName -g $ResourceGroupName -l $DataLocation  -u $SQLLogin1 -p $Password --ssl-enforcement Enabled --sku-name "GP_GEN5_2" # (The --sku-name parameter is sometimes required for setting up the server.  If the command fails, try disabling that parameter.)
az mysql server list --resource-group $ResourceGroupName --output table
az mysql db list -g $ResourceGroupName -s $MySQLServerName | ConvertFrom-Json | Format-Table Name, ResourceGroup, Type

### Configure MySQL Server Firewall
az mysql server firewall-rule create -s $MySQLServerName -g $ResourceGroupName -n "ClientIP1" --start-ip-address $ExternalIP --end-ip-address $ExternalIP
az mysql server firewall-rule create -s $MySQLServerName -g $ResourceGroupName -n "AllowAllWindowsAzureIps" --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

### Install MySQL Python Connector  (Not needed for lab exercise but useful for Python developers.  Might require a virtual environment (virtualenv).)
# pip install mysql-connector


### Log VM Information and delete the Resource Group
"Azure MySQL Server Name :  " + $MySQLServerFQDN >> $WorkFolder$logFilePrefix$logFileSuffix
"Resource Group Name     :  " + $ResourceGroupName + "   # Delete the Resource Group to remove all Azure resources created by this script (e.g. Remove-AzureRMResourceGroup -Name $ResourceGroupName -Force)"  >> $WorkFolder$logFilePrefix$logFileSuffix
$EndTime = Get-Date ; $et = "AzureMySQL" + $EndTime.ToString("yyyyMMddHHmm")
"End Time:   " + $EndTime >> $WorkFolder$logFilePrefix$logFileSuffix
"Duration:   " + ($EndTime - $StartTime).TotalMinutes + " (Minutes)" >> $WorkFolder$logFilePrefix$logFileSuffix
Rename-Item -Path $WorkFolder$logFilePrefix$logFileSuffix -NewName $et$logFileSuffix
### Remove-AzureRMResourceGroup -Name $ResourceGroupName -Verbose -Force         # az group delete --name $ResourceGroupName
### Clear-Item WSMan:\localhost\Client\TrustedHosts -Force
### pip install --upgrade pandas, pandas_datareader, scipy, matplotlib, pyodbc, pycountry, azure
### Import-Module servermanager
### Add-WindowsFeature telnet-client
### telnet $MySQLServerFQDN 3306
