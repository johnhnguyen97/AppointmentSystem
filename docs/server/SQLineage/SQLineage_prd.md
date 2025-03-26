# SQLLineage Documentation

## Core Components

### MetaDataProvider
- Base class used to provide metadata like table schema
- Used for parsing SQL queries and determining column lineage
- Helps analyze queries like:
```sql
INSERT INTO db1.table1
SELECT c1
FROM db2.table2 t2
JOIN db3.table3 t3 ON t2.id = t3.id
```

### Models

#### Schema Class
```python
class Schema(name: str | None = None)
```
- Data class for Schema representation
- Parameters:
  - name: schema name

#### Table Class
```python
class Table(name: str, schema: Schema = Schema: <default>, **kwargs)
```
- Data class for Table representation
- Parameters:
  - name: table name
  - schema: schema as defined by Schema

#### SubQuery Class
```python
class SubQuery(subquery: Any, subquery_raw: str, alias: str | None)
```
- Data class for SubQuery representation
- Parameters:
  - subquery: subquery content
  - subquery_raw: raw subquery string
  - alias: subquery alias name

#### Column Class
```python
class Column(name: str, **kwargs)
```
- Data class for Column representation
- Parameters:
  - name: column name
  - parent: Table or SubQuery reference
  - Additional keyword arguments

## Analyzer Components

### LineageAnalyzer
- Abstract class for core SQL analysis
- Each parser implementation inherits this class
- Implements analyze method for statement processing
- Stores results in StatementLineageHolder

### Runner
LineageRunner is the entry point for SQLLineage core processing:
1. Splits SQL statements into individual statements
2. Analyzes each statement using LineageAnalyzer
3. Assembles results into SQLLineageHolder

## Dialect-Awareness Features

### Key Capabilities
- Syntax validation
- Dialect-specific syntax support:
  - MSSQL assignment operators
  - Snowflake MERGE statements
  - Identifier quote characters
  - Reserved keywords handling
  - Custom functions (Presto UNNEST, Snowflake GENERATOR)

### Usage Example
```bash
sqllineage -f test.sql --dialect=ansi
```

```python
from sqllineage.runner import LineageRunner
sql = "select * from dual"
result = LineageRunner(sql, dialect="ansi")
```

## Column-Level Lineage

### Design Principles
1. Static code analysis focused
2. Tolerant of missing information
3. Unified DAG with table-level lineage
4. Support for metadata enhancement

### Implementation Features
- Handles column aliases
- Processes subqueries
- Manages table joins
- Supports multiple statement analysis

### MetaData Providers

#### DummyMetaDataProvider
```python
class DummyMetaDataProvider(metadata: dict[str, list[str]] | None = None)
```
- Basic provider for testing
- Accepts metadata as dictionary
- Example:
```python
metadata = {"main.bar": ["col1", "col2"]}
provider = DummyMetaDataProvider(metadata)
```

#### SQLAlchemyMetaDataProvider
```python
class SQLAlchemyMetaDataProvider(url: str, engine_kwargs: dict[str, Any] | None = None)
```
- Queries metadata from databases
- Uses SQLAlchemy for connectivity
- Supports multiple database types

### Configuration Options

#### Environment Variables
- SQLLINEAGE_DEFAULT_SCHEMA
- SQLLINEAGE_DIRECTORY
- SQLLINEAGE_LATERAL_COLUMN_ALIAS_REFERENCE
- SQLLINEAGE_TSQL_NO_SEMICOLON

#### Runtime Configuration
```python
from sqllineage.config import SQLLineageConfig

with SQLLineageConfig(DEFAULT_SCHEMA="ods"):
    print(LineageRunner("select * from test").source_tables)
```

## Advanced Usage

### Multiple Statement Analysis
```bash
sqllineage -e "insert into db1.table1 select * from db2.table2; insert into db3.table3 select * from db1.table1;"
```

### Column-Level Analysis
```bash
sqllineage -f test.sql -l column
```

### Visualization
```bash
sqllineage -g -f test.sql
```
- Generates interactive graph visualization
- Shows table and column-level relationships
- Displays DAG representation of lineage

## Best Practices
1. Always specify dialect when possible
2. Use metadata providers for accurate column lineage
3. Leverage visualization for complex queries
4. Configure default schema appropriately
5. Utilize verbose mode for detailed analysis
