# Process all the employee records in the "tbl" files and merge them in a csv file
import glob, pandas as pd

allfiles = glob.glob("*.tbl")
columns = ['EmployeeID','LastName','FirstName','HireDate','Salary','FullName']
alldata = pd.DataFrame(columns=columns)

for file in allfiles:
   names = ['EmployeeID','LastName','FirstName','HireDate','Salary']
   data = pd.read_csv(file, index_col = None, names = names, header = 0)
   data['FullName'] = data['LastName'] + "; " + data['FirstName'] 
   alldata = alldata.append(data)


alldata.to_csv('allemployees.csv',index=False,header=["CompanyID","LastName","FirstName","HireDate","Salary","FullName"])





