# LocalDataAI

LocalDataAI is a local-first AI data intelligence platform designed to translate natural-language questions into structured, validated data operations.

The project is being built around a key architectural principle:

**the LLM is a reasoning component, not a trusted execution engine.**

Instead of allowing an LLM to directly generate and execute arbitrary SQL, LocalDataAI uses typed intermediate representations, schema awareness, semantic metadata and deterministic execution components.

> Status: early development — core Python architecture and data-catalog foundations are currently being implemented.

## Architecture

The current architecture is evolving toward the following flow:

```text
User Question
      |
      v
Schema Linking
      |
      v
Structured QueryPlan
      |
      v
Validation
      |
      v
Deterministic SQL Compiler
      |
      v
PostgreSQL
      |
      v
QueryResult
```

A future Java/Spring Boot layer will act as the external application gateway, while Python remains responsible for AI, ML and data-intelligence workloads.

```text
Client / UI
     |
     v
Java 25 / Spring Boot
     |
     | HTTP
     v
Python AI Engine
     |
     +-- Schema Linking
     +-- Query Planning
     +-- SQL Compilation
     +-- RAG
     +-- ML
     +-- Local LLMs
     |
     v
PostgreSQL / Documents / Local Models
```

## Why Structured Query Planning?

A central design decision in LocalDataAI is to avoid unrestricted text-to-SQL generation.

A user question such as:

```text
Show the 10 countries with the highest total sales in 2026.
```

is intended to become a typed structure such as:

```json
{
  "kind": "aggregated",
  "table": "sales",
  "filters": [
    {
      "column": "year",
      "operator": "=",
      "value": 2026
    }
  ],
  "dimensions": [
    {
      "column": "country"
    }
  ],
  "measures": [
    {
      "column": "sales",
      "aggregation": "sum"
    }
  ],
  "order_by": [
    {
      "column": "sales",
      "direction": "desc"
    }
  ],
  "limit": 10
}
```

This `QueryPlan` can then be validated before deterministic code generates SQL.

The intended boundary is:

```text
Natural Language
      |
      v
LLM Reasoning
      |
      v
Typed QueryPlan
      |
      v
Validation
      |
      v
Deterministic Execution
```

## Current Project Structure

```text
data-assistant/
|
|-- data_assistant/
|   |
|   |-- __init__.py
|   |-- api.py
|   |-- config.py
|   |-- schema_linker.py
|   |
|   |-- domain/
|   |   |-- __init__.py
|   |   |-- plan.py
|   |   `-- results.py
|   |
|   `-- data/
|       |-- __init__.py
|       |-- catalog.py
|       |-- postgres.py
|       |-- registry.py
|       |-- semantic.py
|       `-- semantic.yaml
|
|-- .env.example
|-- .gitignore
|-- pyproject.toml
`-- README.md
```

## Implemented Components

### Configuration

Application configuration is managed with `pydantic-settings`.

Configuration can be supplied through environment variables or a local `.env` file.

Example:

```env
APP_NAME=Local Data Assistant
APP_VERSION=0.0.1

API_HOST=0.0.0.0
API_PORT=8000

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=data_assistant
POSTGRES_USER=data_assistant
POSTGRES_PASSWORD=change_me

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

DEBUG=true
```

The real `.env` file is excluded from version control.

`.env.example` acts as the configuration template.

## FastAPI Service

The Python engine exposes an HTTP interface using FastAPI.

The currently implemented endpoint is:

```text
GET /health
```

Start the development server with:

```bash
uvicorn data_assistant.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Domain Model

The query domain is represented with strict Pydantic models.

The current domain includes:

```text
Filter
Dimension
Measure
Sort
QueryPlan
QueryResult
```

Unknown fields are forbidden and query-plan objects are immutable after creation.

This provides a strict contract between future LLM reasoning and deterministic application logic.

### Filter

Represents a condition such as:

```text
year = 2026
```

Supported operators currently include:

```text
=
!=
>
>=
<
<=
in
not_in
contains
```

### Dimension

Represents a grouping dimension such as:

```text
country
department
year
```

### Measure

Represents an aggregation such as:

```text
SUM(sales)
AVG(salary)
COUNT(order_id)
```

Supported aggregations currently include:

```text
sum
avg
count
min
max
```

### Sort

Represents ascending or descending ordering.

### QueryPlan

Combines filters, dimensions, measures, sorting and result limits into one validated intermediate representation.

## Data Catalog

LocalDataAI maintains an internal representation of the connected database:

```text
Catalog
   |
   +-- Table
         |
         +-- Column
```

A `Column` can contain metadata such as:

```text
name
data type
description
unit
synonyms
sample values
distinct count
null count
minimum
maximum
uniqueness
```

The catalog separates technical database metadata from business semantics.

## PostgreSQL Schema Discovery

PostgreSQL metadata is discovered through `information_schema`.

The current implementation discovers:

```text
tables
columns
database data types
```

PostgreSQL-specific data types are normalized into a smaller semantic type system:

```text
smallint / integer / bigint
numeric / decimal / real
double precision
        |
        v
     number
```

```text
date / timestamp / time
        |
        v
      date
```

```text
boolean
   |
   v
 bool
```

Other values currently fall back to:

```text
text
```

## Semantic Metadata

Database schemas frequently contain technical names that do not fully describe their business meaning.

LocalDataAI therefore supports a separate semantic metadata layer.

Example:

```yaml
tables:
  sales:
    description: "Sales transactions"
    synonyms:
      - transactions

    columns:
      revenue:
        description: "Net sales revenue"
        synonyms:
          - sales
          - turnover
        unit: "EUR"
```

This metadata is merged with the automatically discovered PostgreSQL catalog.

Technical metadata therefore comes from the database, while domain-specific descriptions and synonyms can be curated independently.

## Catalog Registry

The enriched catalog is cached in memory.

```text
PostgreSQL
     |
     v
Raw Catalog

semantic.yaml
     |
     v
Semantic Metadata

     |
     v

Enriched Catalog
     |
     v
Cached Registry
```

The cache can be explicitly refreshed when the underlying schema or semantic metadata changes.

## Schema Linking

Initial schema-linking infrastructure is currently being implemented.

The first stage performs deterministic text normalization and exact matching against database names and curated synonyms.

Example:

```text
User question:
"Show turnover by country"
```

Semantic metadata:

```text
column: revenue
synonyms:
- sales
- turnover
```

The schema linker can therefore associate the user's word `turnover` with the physical database column `revenue`.

Future schema-linking stages will include fuzzy and semantic matching.

## Current Technology Stack

Python:

```text
Python 3.11+
FastAPI
Pydantic
Pydantic Settings
Psycopg
PyYAML
```

Dependencies already prepared for later stages include:

```text
SQLGlot
DuckDB
Pandas
NumPy
scikit-learn
UMAP
RapidFuzz
PyMuPDF
OpenPyXL
Ollama integration
TOON
```

Not all dependencies listed above are implemented in the application yet.

## Roadmap

Planned components include:

```text
Advanced schema linking
Value indexing
LLM query planner
Ollama integration
QueryPlan validation
Deterministic SQL compiler
SQL safety layer
PostgreSQL execution
Result grounding
Natural-language response generation
Document ingestion
RAG
Excel ingestion
Feedback and evaluation
Observability
Docker deployment
Java 25 / Spring Boot gateway
CI/CD
```

## Design Principles

LocalDataAI is being developed around several principles:

**Local-first execution**  
Business data and AI workloads should be able to remain on-premise.

**Structured LLM outputs**  
LLMs should produce constrained intermediate representations instead of arbitrary executable instructions.

**Deterministic execution**  
Critical operations such as SQL generation should eventually be handled by deterministic code.

**Schema grounding**  
The AI should reason over actual database metadata rather than inventing tables or columns.

**Semantic separation**  
Physical database structure and business meaning are maintained as separate but composable layers.

**Fail safely**  
Invalid plans should fail validation before reaching an execution layer.

## Development

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project:

```bash
pip install -e .
```

Start the API:

```bash
uvicorn data_assistant.api:app --reload
```

## Project Status

LocalDataAI is currently under active development.

The current repository represents the foundation of the Python AI/data engine rather than a finished end-user application.