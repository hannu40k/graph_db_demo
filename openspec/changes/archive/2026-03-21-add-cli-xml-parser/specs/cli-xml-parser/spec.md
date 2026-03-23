## ADDED Requirements

### Requirement: XML Graph Parsing
The system SHALL provide an `XmlGraphParser` class in `app/services/graph_service.py`
that parses a directed weighted graph from an XML file into a Python `Graph` domain
object. Parsing SHALL use `lxml.etree.iterparse` for streaming support.

#### Scenario: Valid XML file produces correct Graph
- **WHEN** `XmlGraphParser.from_xml_file` is called with a valid XML file path
- **THEN** a `Graph` object is returned with correct id, name, nodes, and edges
- **AND** edge costs default to 0.0 when the `<cost>` element is absent

#### Scenario: Invalid XML raises GraphXmlParseError
- **WHEN** `XmlGraphParser.from_xml_file` is called with an XML file that violates any validation rule
- **THEN** a `GraphXmlParseError` is raised with a descriptive message

### Requirement: XML Validation Rules
The parser SHALL enforce the following validation rules and raise `GraphXmlParseError` for each violation:

#### Scenario: Missing graph id or name
- **WHEN** the `<graph>` element lacks an `<id>` or `<name>` child
- **THEN** `GraphXmlParseError` is raised

#### Scenario: Edges group before nodes group
- **WHEN** the `<edges>` group appears in the XML before the `<nodes>` group
- **THEN** `GraphXmlParseError` is raised

#### Scenario: Empty nodes group
- **WHEN** the `<nodes>` group contains no `<node>` elements
- **THEN** `GraphXmlParseError` is raised

#### Scenario: Duplicate node ids
- **WHEN** two `<node>` elements within `<nodes>` share the same `<id>` value
- **THEN** `GraphXmlParseError` is raised

#### Scenario: Edge with multiple from or to elements
- **WHEN** an edge `<node>` within `<edges>` contains more than one `<from>` or more than one `<to>` element
- **THEN** `GraphXmlParseError` is raised

#### Scenario: Edge references undefined node
- **WHEN** an edge `<from>` or `<to>` value does not match any defined node id
- **THEN** `GraphXmlParseError` is raised

#### Scenario: Negative edge cost
- **WHEN** an edge `<cost>` element contains a negative number
- **THEN** `GraphXmlParseError` is raised

### Requirement: CLI Parse Graph Command
The system SHALL provide a `parse_graph` CLI command in `app/cli/parse_graph.py`
implemented with Click, accepting `--file-path`, `--print`, and `--insert` options.

#### Scenario: Print parsed graph
- **WHEN** `parse_graph --file-path=<path> --print` is invoked with a valid XML file
- **THEN** the parsed `Graph` is output as pretty-printed JSON to stdout
- **AND** the command exits with code 0

#### Scenario: Insert graph into database
- **WHEN** `parse_graph --file-path=<path> --insert` is invoked with a valid XML file
- **THEN** the graph is inserted into the database via `GraphService.insert_graph`
- **AND** the inserted graph id is printed to stdout
- **AND** the command exits with code 0

#### Scenario: Parse error exits with code 1
- **WHEN** `parse_graph --file-path=<path>` is invoked with an invalid XML file
- **THEN** the error message is printed to stderr
- **AND** the command exits with code 1

### Requirement: Domain Types Module
The system SHALL provide `app/types.py` with Pydantic `BaseModel` classes `Graph`,
`Node`, and `Edge` as the intermediate representation between XML parsing and database
persistence.

#### Scenario: Edge cost defaults to zero
- **WHEN** an `Edge` is constructed without a `cost` argument
- **THEN** `cost` defaults to `0.0`

#### Scenario: Edge cost must be non-negative
- **WHEN** an `Edge` is constructed with a negative `cost`
- **THEN** a Pydantic `ValidationError` is raised

### Requirement: GraphService insert_graph accepts domain type
The `GraphService.insert_graph` method SHALL accept a `Graph` domain type (from
`app/types.py`) and convert it to database models internally before persisting.

#### Scenario: Insert Graph domain object
- **WHEN** `GraphService.insert_graph(graph: Graph)` is called with a valid `Graph`
- **THEN** the graph, its nodes, and its edges are persisted to the database
- **AND** the inserted graph id is returned as a string
