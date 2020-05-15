import mysql.connector
from mysql.connector import errorcode

# Obtain connection string information from the portal
config = {
  "host":"mysql200817.mysql.database.azure.com",
  "user":"SQLLogin1@mysql200817",
  "password":"Password1234",
  "database":"mysqldb1"
}

tablename = "employees"
tablerecords = "allemployees.csv"
newuser="SQLLogin2@mysql200817"
newpassword = config["password"]

# Construct connection string
try:
   conn = mysql.connector.connect(**config)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Access denied.  Verify the login credentials")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("The database does not exist")
  else:
    print(err)
else:
  cursor = conn.cursor()

createuser = "CREATE USER " + newuser + " IDENTIFIED BY " + "'" + newpassword + "'" + ";"
cursor.execute(createuser)

databasegrantnewuser = "GRANT ALL PRIVILEGES ON " + config["database"] + " TO " + newuser + " IDENTIFIED BY " + "'" + newpassword +"'" + ";"
cursor.execute(databasegrantnewuser)
databasegrantuser = "GRANT ALL PRIVILEGES ON " + config["database"] + " TO " + config["user"] + " IDENTIFIED BY " + "'" + config["password"] +"'" + ";"
cursor.execute(databasegrantuser)

# Create Employees Table
tablecreate = "CREATE TABLE " + tablename + " (companyid VARCHAR(50), lastname VARCHAR(50), firstname VARCHAR(50), hiredate VARCHAR(50), salary INTEGER, fullname VARCHAR(50));"
cursor.execute(tablecreate)

# cursor.execute("SET @@global.local_infile = 1;")
#cursor.execute("\"\"\"LOAD DATA INFILE allemployees.csv INTO TABLE employees6 FIELDS TERMINATED BY \',\' ENCLOSED BY \'\"\' LINES TERMINATED BY '\\n\' IGNORE 1 ROWS;;\"\"\"")
#insertrecords = "\"\"\"LOAD DATA INFILE " + tablerecords + " INTO TABLE " + tablename + " FIELDS TERMINATED BY \',\'  ENCLOSED BY \'\"\' LINES TERMINATED BY \'\\\n\' IGNORE 1 ROWS;;\"\"\""
#cursor.execute(insertrecords)
#tablequery = "SELECT * FROM " + tablename
#cursor.execute(tablequery)
#records = cursor.fetchall()

# Close Connection
conn.commit()
cursor.close()
conn.close()


