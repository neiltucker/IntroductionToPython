# This script will create an "Employee Table" with randomized employee names and hire dates and export to a CSV file.
# Change the rows variable to control the number of rows exported.
# pip install --upgrade names, pandas, pandas_datareader, scipy, matplotlib, pyodbc, pycountry, azure

### This looping operation will install required modules that are not already configured.
import importlib, os, sys
packages = ['numpy', 'pandas']
for package in packages:
  try:
    module = importlib.__import__(package)
    globals()[package] = module
  except ImportError:
    cmd = 'pip install --user ' + package
    os.system(cmd)
    module = importlib.__import__(package)

import names, random, datetime, numpy as np, pandas as pd, time, string, csv
rows = 10000
employeeid = np.array(range(1,10001))
lastname = np.array([''.join(names.get_last_name()) for _ in range(rows)])
firstname = np.array([''.join(names.get_first_name()) for _ in range(rows)])
nowdate = datetime.date.today()
dateofbirth = np.array([nowdate - datetime.timedelta(days=(random.randint(7300,21900))) for _ in range(rows)])
hiredate = np.array([nowdate - datetime.timedelta(days=(random.randint(30,3650))) for _ in range(rows)])
salary = np.array([random.randrange(36000,126000,3000) for _ in range(rows)])
locationid = np.array([random.randint(1,8) for _ in range(rows)])
departmentid = np.array([random.randint(1,5) for _ in range(rows)])
inputzip = zip(employeeid,lastname,firstname,dateofbirth,hiredate,salary,locationid,departmentid)
inputlist = list(zip(employeeid,lastname,firstname,dateofbirth,hiredate,salary,locationid,departmentid))
df = pd.DataFrame(inputlist)
df.to_csv('employeetable.csv',index=False,header=["EmployeeID","LastName","FirstName","DateOfBirth","HireDate","Salary","LocationID","DepartmentID"])
