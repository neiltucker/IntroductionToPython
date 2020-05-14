import pyodbc
server = 'azsrvazdb01.database.windows.net'
database = 'database001'
username = 'sqllogin1'
password = 'Password1234'
driver= '{SQL Server}'
driver1= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER=driver;SERVER=server;PORT=1433;DATABASE=database;UID=username;PWD=password')
cursor = cnxn.cursor()
cursor.execute("SELECT * From dbo.employees")
row = cursor.fetchone()
while row:
    print (str(row[0]) + " " + str(row[1]))
    row = cursor.fetchone()

