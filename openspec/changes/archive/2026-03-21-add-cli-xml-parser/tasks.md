## Execution Order

Tasks are grouped by dependency. Complete groups in order. Within a group, items can be parallelized unless noted.

## 1. Domain Types

- [x] 1.1 Create `app/types.py` with `Node`, `Edge`, `Graph` Pydantic `BaseModel` classes
  - `Edge.cost: float = Field(default=0.0, ge=0)` — enforce non-negative via Pydantic
  - `Edge.from_node: str` and `Edge.to_node: str` (not `from`/`to` — avoid Python keyword)

## 2. XML Parser (depends on: 1)

- [x] 2.1 Add `GraphXmlParseError(Exception)` to `app/services/graph_service.py`
- [x] 2.2 Add `XmlGraphParser` class to `app/services/graph_service.py` (no constructor args)
- [x] 2.3 Implement `XmlGraphParser.from_xml_file(file_path: str) -> Graph` using `lxml.etree.iterparse`
  - Track state: `in_nodes_group`, `in_edges_group`, current element buffer
  - Disambiguate `<nodes><node>` (graph node) from `<edges><node>` (edge) via group flag
  - Add comment: iterparse caveat — ordering validation (nodes before edges) happens inline during iteration, not before starting work
- [x] 2.4 Implement all 7 validation rules (raise `GraphXmlParseError` on failure):
  - `<graph>` must have `<id>` and `<name>`
  - `<nodes>` must appear before `<edges>` in document order
  - `<nodes>` must contain at least one `<node>`
  - All node `<id>` values must be unique
  - Each edge must have exactly one `<from>` and one `<to>` tag
  - Edge `<from>` and `<to>` must reference defined node ids
  - `<cost>` must be a non-negative float if present

## 3. GraphService Update (depends on: 1)

- [x] 3.1 Update `GraphService.insert_graph` signature from `insert_graph(graph_db: GraphDB) -> str` to `insert_graph(graph: Graph) -> str`
  - Internally convert `Graph` → `GraphDB`, `Node` → `NodeDB`, `Edge` → `EdgeDB`
  - Keep the same DB persistence logic (add, flush, commit, refresh)

## 4. CLI Application (depends on: 2, 3)

- [x] 4.1 Implement `app/cli/parse_graph.py` with Click:
  - `--file-path` (required, `str`): path to XML file
  - `--print` (flag): output parsed `Graph` as pretty-printed JSON to stdout
  - `--insert` (flag): insert into DB via `GraphService`; print inserted graph id
  - On `GraphXmlParseError`: print error message to stderr, `sys.exit(1)`
  - On `--insert`: use `next(get_session())` from `app/db.py`
- [x] 4.2 Register CLI entrypoint in `pyproject.toml` under `[project.scripts]`

## 5. Tests (depends on: 2, 3, 4)

- [x] 5.1 Create `app/cli/tests/__init__.py` (if not already present — check first)
- [x] 5.2 Write `app/cli/tests/test_xml_parser.py`:
  - 1 test: valid `samples/good/sample_graph_1.xml` → correct `Graph` object (check id, name, node count, edge count, edge cost, self-loop edge)
  - 9 tests: one per `samples/invalid/sample_graph_invalid_N.xml`, each asserting `GraphXmlParseError` is raised with an appropriate message
- [x] 5.3 Write `app/cli/tests/test_parse_graph_cli.py` using Click `CliRunner`:
  - `--print` with valid XML → exit code 0, stdout is valid JSON with correct structure
  - `--insert` with valid XML → calls `GraphService.insert_graph` (mock session), prints graph id
  - Invalid XML file → exit code 1, error message in output
  - Missing `--file-path` → Click usage error
