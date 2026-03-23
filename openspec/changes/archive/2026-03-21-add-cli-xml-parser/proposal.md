# Change: Add CLI XML Graph Parser (Component 2)

## Why

The project needs a CLI ingestion tool to parse directed weighted graphs from XML files
and load them into the PostgreSQL database that the FastAPI backend queries. Without this
tool, there is no way to populate the database with graph data.

## What Changes

- Add `app/types.py` with pure Python Pydantic domain types: `Graph`, `Node`, `Edge`
- Add `XmlGraphParser` class to `app/services/graph_service.py` with `from_xml_file(file_path: str) -> Graph` method using `lxml.etree.iterparse`
- Update `GraphService.insert_graph` to accept `Graph` (Python type) instead of `GraphDB` (**BREAKING** to existing method signature, safe because no callers yet)
- Implement `app/cli/parse_graph.py` Click CLI with `--file-path`, `--print`, `--insert` options
- Add `GraphXmlParseError` custom exception for all XML validation failures
- Add unit tests in `app/cli/tests/test_xml_parser.py` (9 invalid samples + 1 valid)
- Add CLI tests in `app/cli/tests/test_parse_graph_cli.py`

## Impact

- Affected specs: `cli-xml-parser` (new capability)
- Affected code: `app/types.py` (new), `app/services/graph_service.py` (extended), `app/cli/parse_graph.py` (new), `app/cli/tests/` (new tests)
