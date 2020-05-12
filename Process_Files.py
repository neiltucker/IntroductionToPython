# Process all the employee records in the "tbl" files and merge them in a csv file
import glob, pandas as pd

allfiles = glob.glob("*.tbl")
columns = ['EmployeeID','LastName','FirstName','HireDate','Salary']
alldata = pd.DataFrame(columns=columns)

for file in allfiles:
   data = pd.read_csv(file, index_col = None, names = columns, header = 0)
   alldata = alldata.append(data)


alldata.to_csv('allemployees.csv',index=False,header=["EmployeeID","LastName","FirstName","HireDate","Salary"])





