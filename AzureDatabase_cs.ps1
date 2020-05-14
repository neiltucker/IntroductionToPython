### Create an Azure SQL server and databases using the Azure Cloud Shell (cs).  If your subscription resources allow, keep these databases for future labs.
### Configure Objects & Variables
Set-StrictMode -Version 2.0
$SubscriptionName = (Get-AzureRMSubscription)[0].Name                                 # Replace with the name of your preferred subscription
$CloudDriveMP = (Get-CloudDrive).MountPoint
$WorkFolder = "/home/$env:USER/"
Set-Location $WorkFolder
$ExternalIP = ((Invoke-WebRequest -URI IPv4.Icanhazip.com -UseBasicParsing).Content).Trim()                                          # You may substitute with the Internet IP of your computer
# $ExternalIP = ((Invoke-WebRequest -Uri checkip.dyndns.org -UseBasicParsing).ParsedHtml.body.innerHtml -replace '^\D+').Trim()        # You may substitute with the Internet IP of your computer
If (Get-Module -ListAvailable -Name SQLServer) {Write-Output "SQLServer module already installed" ; Import-Module SQLServer} Else {Install-Module -Name SQLServer -Force ; Import-Module -Name SQLServer}
$SQLLogin1 = "sqllogin1"
$Password = 'Password1234'
$PW = Write-Output $Password | ConvertTo-SecureString -AsPlainText -Force        # Password for SQL Database server
$SQLCredentials =  (New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $SQLLogin1, $PW)
$Location = "EASTUS"
$NamePrefix = "np" + (Get-Date -Format "HHmmss")
$ResourceGroupName = $NamePrefix.ToLower() + "rg"
$StorageAccountName = $NamePrefix.ToLower() + "sa"     # Must be lower case
$AzureServer = "srv" + $NamePrefix.ToLower()
$AzureServerDNS = $AzureServer + ".database.windows.net"
$AdventureWorksDatabase = "adventureworks"
$DB1Database = "database001"
$AdventureWorksConnectionString = "Server=tcp:$AzureServerDNS;Database=$AdventureWorksDatabase;User ID=$SQLLogin1@$AzureServer;Password=$Password;Trusted_Connection=False;Encrypt=True;"
$DB1ConnectionString = "Server=tcp:$AzureServerDNS;Database=$DB1Database;User ID=$SQLLogin1@$AzureServer;Password=$Password;Trusted_Connection=False;Encrypt=True;"
$SAShare = "SAShare"                                    # Must be lower case
$TMPData = $WorkFolder + "employees.tmp"
$CustomerCSV = $WorkFolder + "customer.csv"


### Log start time of script
$logFilePrefix = "AzureSQL" + (Get-Date -Format "HHmm") ; $logFileSuffix = ".txt" ; $StartTime = Get-Date
"Create Azure Server and Database"   >  $WorkFolder$logFilePrefix$logFileSuffix
"Start Time: " + $StartTime >> $WorkFolder$logFilePrefix$logFileSuffix

### Login to Azure
# Connect-AzureRmAccount
$Subscription = Get-AzureRmSubscription -SubscriptionName $SubscriptionName | Set-AzureRMContext
Register-AzureRmResourceProvider -ProviderNamespace Microsoft.Batch

### Create Resource Group, Storage Account & Storage Account Share
New-AzureRMResourceGroup -Name $ResourceGroupName  -Location $Location
New-AzureRMStorageAccount -ResourceGroupName $ResourceGroupName -Name $StorageAccountName -Location $Location -Type Standard_RAGRS
$StorageAccountKey = (Get-AzureRmStorageAccountKey -ResourceGroupName $ResourceGroupName -Name $StorageAccountName)[0].Value
$StorageAccountContext = New-AzureStorageContext -StorageAccountName $StorageAccountName -StorageAccountKey $StorageAccountKey
$BlobContainer = New-AzureStorageContainer -Name $SAShare.ToLower() -Context $StorageAccountContext -Permission Container -Verbose
$BlobLocation = $BlobContainer.cloudblobcontainer.Uri.AbsoluteUri
Get-ChildItem -File $WorkFolder"employees.*" | Set-AzureStorageBlobContent -Container $SAShare -Context $StorageAccountContext -Force

### Create Azure Database Server
$AzureSQLServer = New-AzureRMSQLServer -ResourceGroupName $ResourceGroupName -ServerName $AzureServer -Location $Location -SqlAdministratorCredentials $SQLCredentials

### Create and Copy Azure Databases
New-AzureRMSQLDatabase -ResourceGroupName $ResourceGroupName -ServerName $AzureServer -DatabaseName $DB1Database -RequestedServiceObjectiveName "S0"
New-AzureRMSQLDatabase -ResourceGroupName $ResourceGroupName -ServerName $AzureServer -DatabaseName $AdventureWorksDatabase -SampleName "AdventureWorksLT" -RequestedServiceObjectiveName "S0"
New-AzureRmSqlDatabaseCopy -ResourceGroupName $ResourceGroupName -ServerName $AzureServer -DatabaseName $AdventureWorksDatabase -CopyResourceGroupName $ResourceGroupName -CopyServerName $AzureServer -CopyDatabaseName "AdventureWorksCopy"

### Create Firewall Rules
New-AzureRmSQLServerFirewallRule -ResourceGroupName $ResourceGroupName -ServerName $AzureServer -FirewallRuleName "RemoteConnection1" -StartIpAddress $ExternalIP -EndIpAddress $ExternalIP
New-AzureRmSQLServerFirewallRule -ResourceGroupName $ResourceGroupName -ServerName $AzureServer -FirewallRuleName "AllowAllWindowsAzureIPs" -StartIpAddress 0.0.0.0 -EndIpAddress 0.0.0.0

### Query Database and Export Table Data
Get-AzureRMSQLServer -ResourceGroupName $ResourceGroupName | Where-Object {$_.ServerName -eq $AzureServer}
Get-AzureRmSQLDatabase -ServerName $AzureServer -ResourceGroupName $ResourceGroupName | Select-Object ServerName, DatabaseName, Location, Status
Invoke-SQLCMD -ConnectionString $AdventureWorksConnectionString -Query "Select * From SalesLT.Customer Where CompanyName > 'W'"          # Run "Import-Module SQLServer" if Invoke-SQLCMD does not work.  Other components may not work if Lab 0, Exercise 1 was not completed.
$CustomerData = Invoke-SQLCMD -ConnectionString $AdventureWorksConnectionString -Query "Select * From SalesLT.Customer"  | Select-Object customerid,firstname,lastname,companyname,salesperson,emailaddress,phone -Last 500
$CustomerData | Export-CSV $CustomerCSV -NoTypeInformation

### Log VM Information and delete the Resource Group
"AZ Database Server Name :  " + $AzureServerDNS >> $WorkFolder$logFilePrefix$logFileSuffix
"AZ Database Name        :  " + $DB1Database >> $WorkFolder$logFilePrefix$logFileSuffix
"Resource Group Name     :  " + $ResourceGroupName + "   # Delete the Resource Group to remove all Azure resources created by this script (e.g. Remove-AzureRMResourceGroup -Name $ResourceGroupName -Force)"  >> $WorkFolder$logFilePrefix$logFileSuffix
$EndTime = Get-Date ; $et = "AzureSQL" + $EndTime.ToString("yyyyMMddHHmm")
"End Time:   " + $EndTime >> $WorkFolder$logFilePrefix$logFileSuffix
"Duration:   " + ($EndTime - $StartTime).TotalMinutes + " (Minutes)" >> $WorkFolder$logFilePrefix$logFileSuffix
Rename-Item -Path $WorkFolder$logFilePrefix$logFileSuffix -NewName $et$logFileSuffix
### Remove-AzureRMResourceGroup -Name $ResourceGroupName -Verbose -Force
### Clear-Item WSMan:\localhost\Client\TrustedHosts -Force

