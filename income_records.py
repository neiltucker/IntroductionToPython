# Work with Per Capita Income Records
import pandas as pd

# the per_capita_income.csv file must be in the current directory
file = "per_capita_income.csv"
data = pd.read_csv(file)
data.columns
data[['Year','Population','Income']]
years = len(data.Income)
average = data.Income.mean()
print("Average income over the last " + str(years) + " years is: " + str(round(average, 0)))








