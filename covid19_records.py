# Download and manipulate Covid19 data
import pandas as pd

url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/05-01-2020.csv"
data = pd.read_csv(url)
data.to_csv('covid19_records.csv')
data.columns
data[['Country_Region','Deaths','Recovered','Active']]
country = data[['Country_Region','Deaths','Recovered','Active']]
country.groupby(['Country_Region']).sum()









