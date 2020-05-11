# Work with Per Capita Income Records using Functions
import pandas as pd
global variable 

# the per_capita_income.csv file must be in the current directory
def income():
   """This function assigns the income dataset to the income variable"""
   global income
   file = "per_capita_income.csv"
   income = pd.read_csv(file)


def printincomeheaders():
   """This function prints the income header data"""
   print(income.columns)
   

def printincome():
   """This function prints the income data"""
   print(income[['Year','Population','Income']])


def printavg():
   """ This function prints the average income for the dataset being used"""
   years = len(income.Income)
   average = income.Income.mean()
   print("Average income over the last " + str(years) + " years is: " + str(round(average, 0)))


income()
printincomeheaders()
printincome()
printavg()







