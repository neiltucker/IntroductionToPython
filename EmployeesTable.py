# This script will create an "Employee Table" with randomized employee names and hire dates and export to a CSV file.
# Change the rows variable to control the number of rows exported.
# pip install --upgrade names, pandas, pandas_datareader, scipy, matplotlib, pyodbc, pycountry, azure

### This looping operation will install the modules not already configured.
import importlib, os, sys, uuid
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
rows = 100
employeeid = np.array([str(uuid.uuid4()) for _ in range(rows)])
lastname = np.array([''.join(names.get_last_name()) for _ in range(rows)])
firstname = np.array([''.join(names.get_first_name()) for _ in range(rows)])
nowdate = datetime.date.today()
hiredate = np.array([nowdate - datetime.timedelta(days=(random.randint(30,180))) for _ in range(rows)])
salary = np.array([str(random.randint(50,100)*1000) for _ in range(rows)])
inputzip = zip(employeeid,lastname,firstname,hiredate,salary)
inputlist = list(zip(employeeid,lastname,firstname,hiredate,salary))
df = pd.DataFrame(inputlist)
df.to_csv('20200507.tbl',index=False,header=["EmployeeID","LastName","FirstName","HireDate","Salary"])
