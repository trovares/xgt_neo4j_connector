#!/usr/bin/env python
# -*- coding: utf-8 -*- --------------------------------------------------===#
#
#  Copyright 2022 Trovares Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#===----------------------------------------------------------------------===#

# This example creates a graph in Oracle SQL, transfers it to xGT, and
# runs a query on it in xGT.

from trovares_connector import ODBCConnector, OracleODBCDriver
import pyodbc
import xgt

xgt_server = xgt.Connection()
xgt_server.set_default_namespace('odbc_test')
xgt_server.drop_namespace('odbc_test', force_drop=True)

connection_string = 'DSN={OracleODBC-19};Server=127.0.0.1;Port=1521;Uid=c##test;Pwd=test;DBQ=XE;'
odbc_driver = OracleODBCDriver(connection_string)
c = ODBCConnector(xgt_server, odbc_driver)
pyodbc_driver = pyodbc.connect(connection_string)
cursor = pyodbc_driver.cursor()

# Uncomment to delete the tables
"""
cursor.execute('DROP TABLE "Person"')
cursor.execute('DROP TABLE "Knows"')
pyodbc_driver.commit()
"""

# Create some ORACLE tables in Oracle SQL.
# The table Person has 1 column called key.
cursor.execute('CREATE TABLE "Person" ("key" INT)')
# The table Knows has 3 columns: Person1, Person2, and Relationship.
cursor.execute('CREATE TABLE "Knows" ("Person1" INT, "Person2" INT, "Relationship" VARCHAR(50))')
cursor.execute('INSERT INTO "Person" VALUES (0)')
for i in range(0, 10):
    cursor.execute(f'INSERT INTO "Person" VALUES ({i + 1})')
    cursor.execute(f'INSERT INTO "Knows" VALUES ({i}, {i + 1}, \'FRIENDS\')')
cursor.execute('INSERT INTO "Knows" VALUES (2, 0, \'PARTNERS\')')
pyodbc_driver.commit()
pyodbc_driver.close()

# Transfer vertices/edges from SQL to xGT:
c.transfer_to_xgt(tables=[('Person', ('key',)),
                          ('Knows', ('Person', 'Person', 'Person1', 'Person2'))
                         ])
# Here we are specifying multiple tables with a mapping syntax to transfer.
# The mapping syntax is given in tuple form as (SQL_TABLE, (XGT_TYPE)) where the tuple format specifies how to map the table to an xGT type.
# The first tuple of tuples is for the Table Person given by (SQL_TABLE, (KEY_COL,)).
# This will create a Vertex frame in xGT titled SQL_TABLE and transfer the whole table to it.
# It will use KEY_COL as the xGT key.
# The second tuple of tuples is for the Table Person given by (SQL_TABLE, (XGT_SRC_FRAME, XGT_TRG_FRAME, SRC_KEY_COL, TRG_KEY_COL))
# This will create an Edge frame in xGT titled SQL_TABLE and transfer the whole table to it.
# It will use XGT_SRC_FRAME and XGT_TRG_FRAME as the Vertex frames for source and target.
# It will use SRC_KEY_COL and TRG_KEY_COL as the key columns for source and target.

xgt_server.drop_frame('Knows')
xgt_server.drop_frame('Person')

# Alternatively these can be transferred via arbitrary queries:
# This is the same as above except it is transferring via an SQL match where it can select any number of columns.
# Here only 1 mapping is specified per match and it will map from the SQL query to mapping.
# The mapping here is given as (XGT_FRAME_NAME, (XGT_TYPE)) where (XGT_TYPE) is the same format above.
# Transfer Person to XgtPerson.
c.transfer_query_to_xgt('SELECT * FROM "Person"', mapping=('XgtPerson', ('key',)))

# Transfer Knows to XgtKnows. This will transfer all the columns returned by the query.
# So Person1, Person2, and Relationship.
c.transfer_query_to_xgt('SELECT * FROM "Knows"', mapping=('XgtKnows', ('XgtPerson', 'XgtPerson', 'Person1', 'Person2')))

xgt_server.drop_frame('XgtKnows')
xgt_server.drop_frame('XgtPerson')

# Alternatively you can create the vertices and vertex frames by specifying easy_edges.
# The key column for the vertex frames will be called key.
c.transfer_query_to_xgt('SELECT * FROM "Knows"', mapping=('XgtKnows', ('XgtPerson', 'XgtPerson', 'Person1', 'Person2')), easy_edges=True)

print("The follow table data was transferred for the Edges: ")
print(xgt_server.get_edge_frame('XgtKnows').get_data())

# Look for a loop
query = 'match(a)-->()-->()-->(a) return a.key'

# Get results with xGT
job = xgt_server.run_job(query)
print('xGT found the following nodes in a triangle: ' + ','.join(str(row[0]) for row in job.get_data()))
xgt_server.drop_namespace('odbc_test', force_drop=True)
