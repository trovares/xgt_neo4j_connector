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

# This example creates a graph in Neo4j, transfers it to xGT, and
# runs the same query in xGT in Neo4j.

from trovares_connector import Neo4jConnector
import xgt

xgt_server = xgt.Connection()
xgt_server.set_default_namespace('neo4j')
database = "test"

c=Neo4jConnector(xgt_server, neo4j_auth=('neo4j', 'foo'), neo4j_database=database)

# Uncomment to delete the database
"""
with c.neo4j_driver.session(database=database) as session:
    session.run("MATCH (n) DETACH DELETE n")
"""

# Create a chain with with a loop in Neo4j
with c.neo4j_driver.session(database=database) as session:
    end = 10
    session.run('create (a:Person{id:0})')
    for i in range(0, end):
        session.run(f'match(a:Person) where a.id = {i} create (a)-[:Knows]->(:Person{{id:{i + 1}}})')
    session.run('match(a:Person), (b:Person) where a.id = 2 and b.id = 0 create (a)-[:Knows]->(b)')

# Transfer graph from Neo4j to xGT
c.transfer_to_xgt(edges=["Knows"])

# Look for the loop
query = "match(a)-->()-->()-->(a) return a.id"

# Get results with Neo4j
with c.neo4j_driver.session(database=database) as session:
    job = session.run(query)
    print("Neo4j found the following nodes in a triangle: " + ','.join(str(row[0]) for row in job))

# Get results with xGT
job = xgt_server.run_job(query)
print("xGT found the following nodes in a triangle: " + ','.join(str(row[0]) for row in job.get_data()))
