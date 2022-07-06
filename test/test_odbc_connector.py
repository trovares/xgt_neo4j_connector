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

import unittest
import time

import xgt
import pyodbc
from trovares_connector import ODBCConnector, SQLODBCDriver

class TestXgtODBCConnector(unittest.TestCase):
  # Print all diffs on failure.
  maxDiff=None
  @classmethod
  def setup_class(cls):
    # Create a connection to Trovares xGT
    cls.xgt = xgt.Connection()
    cls.xgt.set_default_namespace('test')
    cls.odbc_driver, cls.conn = cls._setup_connector()
    return

  @classmethod
  def teardown_class(cls):
    del cls.conn
    cls.xgt.drop_namespace('test', force_drop = True)
    del cls.xgt

  @classmethod
  def _setup_connector(cls):
    connection_string = 'Driver={MariaDB};Server=127.0.0.1;Port=3306;Database=test;Uid=test;Pwd=foo;'
    odbc_driver = pyodbc.connect(connection_string)
    driver = SQLODBCDriver(connection_string)
    conn = ODBCConnector(cls.xgt, driver)
    return (odbc_driver, conn)

  def setup_method(self, method):
    self._erase_mysql_database()

  def teardown_method(self, method):
    self._erase_mysql_database()

  def _erase_mysql_database(self):
    cursor = self.odbc_driver.cursor()
    cursor.execute("DROP TABLE IF EXISTS test")
    self.odbc_driver.commit()
    self.xgt.drop_namespace('test', force_drop = True)

  def test(self):
    cursor = self.odbc_driver.cursor()
    # FIXME(josh) : With multiple rows floats with a bit size of 24 or lower don't work.
    cursor.execute("CREATE TABLE test (TestBool BOOL, TestInt INT, TestBigInt BIGINT, TestFloat FLOAT(24), TestDouble FLOAT(53), "
                   "TestFixedString char(5), TestString varchar(255), TestDecimal DECIMAL(10, 6), TestDate DATE, "
                   "TestDatetime DATETIME, TestTimestamp TIMESTAMP, TestTime TIME, TestYear YEAR)")
    cursor.execute("INSERT INTO test VALUES (True, 32, 5000, 1.7, 1.98, 'vdxs', 'String', 1.78976, '1989-05-06', '1986-05-06 12:56:34', "
                   "'1989-05-06 12:56:34', '12:56:34', 1999)")
    cursor.execute("INSERT INTO test VALUES (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)")
    self.odbc_driver.commit()

    self.conn.transfer_to_xgt(tables = [('test','test')])
    assert self.xgt.get_table_frame('test').num_rows == 2
    print(self.xgt.get_table_frame('test').get_data())
