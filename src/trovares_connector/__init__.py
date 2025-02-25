# -*- coding: utf-8 -*- --------------------------------------------------===#
#
#  Copyright 2018-2023 Trovares Inc.
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

import warnings

warnings.warn(
  "The `trovares-connector` package is deprecated and will no longer receive updates. "
  "Please install `xgt-connector` instead: pip install xgt-connector",
  DeprecationWarning,
  stacklevel=2
)

__ALL__ = [
  'Neo4jConnector',
  'Neo4jDriver',
  'ODBCConnector',
  'SQLODBCDriver',
]

from .neo4j_connector import Neo4jConnector, Neo4jDriver

try:
    from .odbc import ODBCConnector
    from .odbc import SQLODBCDriver
    from .odbc import MongoODBCDriver
    from .odbc import OracleODBCDriver
    from .odbc import SAPODBCDriver
    from .odbc import SnowflakeODBCDriver
except ImportError:
    pass
