# NOT TESTED
# Ref: https://www.oracle.com/technical-resources/articles/database/python-with-database-11g.html
# pip install cx_Oracle

import cx_Oracle
con = cx_Oracle.connect('pythonhol/welcome@127.0.0.1/orcl')
cursor = con.cursor()
cursor.execute('select * from departments order by department_id')
data = cursor.fetchall()
print(data)

# for result in cursor:
#     print(result)

cursor.close()
con.close()