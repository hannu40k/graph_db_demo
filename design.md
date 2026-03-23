Project scope
--------------

The project provides a CLI application for parsing directed weighted graphs defined in XML format, and optionally uploads them to a related database. Additionally, a simple REST API is provided for querying the database and asking questions about the graph. The graphs can contain self-loops.

The project should follow general Python best practices and recommended FastAPI project structure.

Notes about stack and project requirements:

- Use Python version 3.12.3
- For other packages, use latest stable version and pin it.
- The database will be PostgreSQL. It will run in a Docker container.
- The graph will be stored to the database using standard PostgreSQL tables and data types.
- For database migrations, the package `Alembic` should be used.
- For CLI applications, the package `Click` should be used.
- Use Pydantic according to FastAPI best practices.
- Pydantic is also used for JSON parsin and serialization, due to already being tightly packaged with FastAPI.
- lxml is used for XML parsing due to being battle tested, and having good iteration for large files.
- For Python project management, use `uv`.
- For type checking, use `ty` package.
- For linting, use `ruff` package.
- The CLI application and the web backend shall have unit and funcional tests.
- The implemented software components should be modular to allow for easy maintenance and further development and refactoring opportunities. Avoid monolithic modules and files.
- Define a `pyproject.toml` and other necessary files to make the Python project installable.

Other:

Example XML graph files, and input and output JSON files, in directory `samples/`.

Components
------------

The project needs to implement/provide the following software components:

1) Main component: A Python FastAPI web backend

The web backend serves a single REST endpoint: `POST /query/<graph_id>`. It queries the database for the given graph (designated by `<graph_id>`), and computes responses based on the request parameters and the retrieved graph data. The endpoint is public and thus does not need authentication. For database access, it should use the ORM `SQLModel`. The database models/schema should be defined in `app/models.py`. The main web app entrypoint should be in `app/main.py`. Database connection handling should be in `app/db.py`.

Note: The endpoint `POST /query/<graph_id>` deviates from specified `POST /query`, but the spec does explain the task is open ended on purpose. Defining the endpoint as `POST /query/<graph_id>` makes sense because one needs to be able to differentiate between graphs in the DB. Just to really be in line with the spec, a query to `POST /query` should execute the request queries to the latest graph that was inserted in the database.

If a graph `<graph_id>` is not found in the database, return 404 error.

## Web backend design

The backend provides the specified endpoint `POST /query`, and accesses the database to retrieve graph data in order to provide for the received request. The business logic for the endpoint should be defined in `app/services/`, so that it can be re-used elsewhere if necessary. The business logic service should receive the database session as a parameter to provide DB access, i.e.:

```
class GraphService:
    def __init__(self, session: Session):
        self.session = session
```

Note: Remember to use types hints in the actual implementation.

### Backend business logic services

The following services should be defined to provide business logic to the web backend endpoint:

1) `GraphService` in `app/services/graph_service.py

The `GraphService` should provide the following functionality:

- Retrieve a graph and all its nodes and edges by graph id
- A method `get_paths` that accepts a graph (including its nodes and edges) as parameters, plus start and end node id, and returns all defined paths between the requested nodes in the graph according to the API examples provided.
    - If the requested path does not exist, return an empty list [].
    - If start == end, return [[start]] as the list of paths.
    - Do not return self-loops in the results.
    - When requesting the paths between two nodes, and if no paths are found, the value for `paths` should be `false`. Note that this is tricky in Pydantic, and an explicit test case must be defined to ensure this case works correctly.
    - Method signature pseudo-code: `def get_paths(graph: Graph, start: Node, end: Node) -> NodePaths`
- A method `get_cheapest_path` that accepts a graph (including its nodes and edges) as parameters, plus start and end node id, and returns the cheapest path between the requested nodes in the graph according to the API examples provided.
    - If multiple paths receive the same score, return the path with fewest nodes.
    - If multiple paths have equal score and number of nodes, return the first path.
    - When requesting the cheapest path between two nodes, and if the requested path does not exist, the value for `path` should be `false`. Note that this is tricky in Pydantic, and an explicit test case must be defined to ensure this case works correctly.
    - If `start=a` and `end=a`, return ["a"] as the path.
    - Method signature pseudo-code: `def get_cheapest_path(graph: Graph, start: Node, end: Node) -> CheapestPath`

The implementations should use the `networkx` Python package for finding paths in a Graph. Use `networkx` best practices for implementation.

Algorithm choices:
- Finding all paths: Use Depth First Search (DFS). The optimal solution appears to depend heavily on graph characteristics, but DFS enjoys a position as a standard good starting point. Considering that the task spec is not heavy on details, DFS is a reasonable choice.
- Finding cheapest path: Use Dijkstra's algorithm, since all the weights (`cost` attribute) are non-negative, and it should be the most efficient for the purpose, and it does not revisit already visited nodes.

The type `NodePaths` should include the following attrs:
- from: str
- to: str
- paths: list[list[str]]

The type `CheapestPath` should include the following attrs:
- from: str
- to: str
- path: list[str] | bool

Note: Be sure to implement explicit test case for testing behavior and serialization of Pydantic models for attribute `path: list[str] | bool`.

### API input parameters

The endpoint `POST /query` should allow requests that look like the following (multiple example queries):

```
# query 1
{
    "queries": [
        {
            "paths": {
                "start": "a",
                "end": "e"
            }
        },
        {
            "cheapest": {
                "start": "a",
                "end": "e"
            }
        },
        {
            "cheapest": {
                "start": "a",
                "end": "h"
            }
        }
    ]
}

Response should include answers to each requested query.

# query 2
{
    "queries": [
        {
            "paths": {
                "start": "a",
                "end": "e"
            }
        }
    ]
}

Response includes an answer for the requested query.

# query 3
{
    "queries": []
}

Response should be: {
    "answers": []
}
```

Necessary request types should be defined in the FastAPI application accordingly, according to recommended FastAPI best practices.

If a single request query item contains both "paths" and "cheapest" key, raise an error indicating the reason. Each query item should have one or the other key, but not both.

### Output response

The endpoint `POST /query` should return responses that look like the following (multiple exampels, not necessarily matching the exampe requests from above):

```
# answer 1
{
    "answers": [
        {
            "paths": {
                "from": "a",
                "to": "e",
                "paths": [
                    [
                        "a",
                        "b",
                        "e"
                    ],
                    [
                        "a",
                        "e"
                    ]
                ]
            }
        },
        {
            "cheapest": {
                "from": "a",
                "to": "e",
                "path": [
                    "a",
                    "e"
                ]
            }
        },
        {
            "cheapest": {
                "from": "a",
                "to": "h",
                "path": false
            }
        }
    ]
}

# answer 2
{
    "answers": [
        {
            "paths": {
                "from": "a",
                "to": "e",
                "paths": [
                    [
                        "a",
                        "b",
                        "e"
                    ],
                    [
                        "a",
                        "e"
                    ]
                ]
            }
        },
    ]
}

# answer 3
{
    "answers": [
        {
            "paths": {
                "from": "a",
                "to": "e",
                "paths": false
            }
        },
    ]
}
```

Necessary response types should be defined in the FastAPI application accordingly, according to recommended FastAPI best practices.

The tests should include functional tests that call the `POST /query/<graph_id>` endpoint. See samples in `samples/good/` directory for graph payloads that can be loaded into the database, and example requests and responses. The tests should utilize a real PostgreSQL database as a backend, using a throwaway database during tests.

2) Main component: A CLI application for parsing XML files that model directed graphs, and optionally uploads them into a database.

A CLI application for parsing XML files that model directed graphs, into Python objects (Pydantic) and returns the parsed data. With additional parameters, the parsed result is printed.

The main logic for parsing the XML (given as a string) should be placed into a utility function in a library module so that in can be re-used elsewhere. The CLI application will make use of this module.

With an optional parameter, the CLI application will upload the parsed graph into a database. Previously defined DB models in `app/models.py` should be reused for this purpose, as well as the database connection session that is already defined for the web backedn.

The Python package `lxml` should be used for parsing the XML file. Use `etree.iterparse` to accommodate for reading very big files. Acknowledge in comments that this comes with the caviat that validating the order of encountered elements (nodes group must be first, then edges group) will happen while iterating, and not done before starting doing the work.

The CLI application code should live in `app/cli/parse_graph.py`. It should take the following parameters:
- `--file-path=str` (mandatory) File path to the XML file to parse
- `--print` (optional) Print the parsed Graph data
- `--insert` (optional) Insert the parsed Graph data into the database

The business logic for parsing the Graph XML into Python types should be in `app/services/graph_service.py`. If a suitable class exists already, extend it, otherwise define a new one.

The service class should provide the following functionality:
- Parse Graph from XML file and return the Python objects representing the graph
    - Method signature pseudo-code: `def from_xml_file(file_path: str) -> Graph`
- Insert the Graph into the database, returns the id of the inserted row.
    - Method signature pseudo-code: `def insert_graph(graph: Graph) -> str`

When parsing the XML file, the parser logic must include the following validations:
- There must be an <id> and <name> for the <graph> .
- Validate that the <nodes> group will always come before the <edges> group.
- There must be at least one <node> in the <nodes> group.
- All nodes must have different <id> tags.
- For every <edge> , there must be a single <from> tag and a single <to> tag, corresponding to nodes that must have been defined before.
- The <cost> tag is optional and can provide an arbitrary non-negative floating-point number. If it is not present, the cost defaults to zero.

Implement also unit tests for the parsing logic. Each of the above validations must have at least one test case. See example invalid XML payload files in `samples/invalid/` directory for input data for the tests.

Note also especially that the XML uses <node> elements inside <edges>, not <edge> elements. The parser needs to be aware that `<edges><node>` means "edge", not a graph node.


3) Main component: Provide a SQL script that can find cycles in the provided SQL schema.

Find cycles: Implement an SQL query (SQL99 or PL/pgSQL) that finds cycles in a given graph according to your schema.

The CLI application should live in `sql/detect_cycles.sql`. The SQL query should be raw SQL.

To facilitate dev and testing, implement also a script in `sql/insert_graph_with_cycles_1.sql` and `sql/insert_graph_with_cycles_2.sql` that populates the DB with sample graphs with some nodes and edges, that have cycles in them.


## Graph Python types

Below are proposed Python types for representing a parsed Graph from XML.

The type `Graph` should have attributes:
- id: str
- name: str
- nodes: list[Node]
- edges: list[Edge]

The type `Node` should have attributes:
- id: str
- name: str

The type `Edge` should have attributes:
- id: str
- from_node: str
- to_node: str
- cost: float (restriction: cost >= 0, default: 0 if not provided)

## Proposed SQL schema.

Review the below schema and ensure it fits the described use cases. Ask questions for clarifications if necessary, and point out improvements. Try to keep it simple.

Equivalent SQLModel types should be defined for accessing the database from Python web backend and CLI applications. Place the DB types in `app/models.py`.

```
CREATE TABLE graph (
    id VARCHAR(32) PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE node (
    id VARCHAR(32) NOT NULL,
    graph_id VARCHAR(32) NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, graph_id),
    FOREIGN KEY (graph_id) REFERENCES graph(id)
);

CREATE INDEX idx_node_graph_id ON node(graph_id);

CREATE TABLE edge (
    id VARCHAR(32) NOT NULL,
    graph_id VARCHAR(32) NOT NULL,
    from_node_id VARCHAR(32) NOT NULL,
    to_node_id VARCHAR(32) NOT NULL,
    cost NUMERIC,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, graph_id),

    FOREIGN KEY (graph_id) REFERENCES graph(id),
    FOREIGN KEY (from_node_id, graph_id) REFERENCES node(id, graph_id),
    FOREIGN KEY (to_node_id, graph_id) REFERENCES node(id, graph_id)
);

CREATE INDEX idx_edge_graph_id ON edge(graph_id);
CREATE INDEX idx_edge_from_graph ON edge(from_node_id, graph_id);
CREATE INDEX idx_edge_from_graph ON edge(to_node_id, graph_id);
```

## Proposed project structure

.
├── alembic                  # DB migration files generated by alembic.
├── app
│   ├── cli
│   │   ├── detect_cycles.py # CLI application for detecting cycles in a given graph
│   │   └── parse_graph.py   # CLI application for parsing graphs in XML files and uploading to DB
│   ├── db.py                # Database connection types
│   ├── main.py              # Main entrypoint for web backend app
│   ├── models.py            # Database models (SQLModel)
│   └── services             # Business logic for web backend and CLI applications
│       └── graph_service.py # Business logic for Graph processing
└── samples                            # Sample XML and input and output files to the `POST /query` endpoint.
    ├── good                           # Samples with valid XML and requests/responses.
    │   ├── sample_graph_1_input.json
    │   ├── sample_graph_1_output.json
    │   ├── sample_graph_1.xml
    │   ├── sample_graph_3_input.json
    │   ├── sample_graph_3_output.json
    │   └── sample_graph_3.xml
    └── invalid                       # Samples with XML graphs that are invalid for one reason or another (comment inside the file explains reason.)
        ├── sample_graph_invalid_1.xml
        ├── sample_graph_invalid_2.xml
        ├── sample_graph_invalid_3.xml
        ├── sample_graph_invalid_4.xml
        ├── sample_graph_invalid_5.xml
        ├── sample_graph_invalid_6.xml
        ├── sample_graph_invalid_7.xml
        ├── sample_graph_invalid_8.xml
        └── sample_graph_invalid_9.xml

## Alembic use

Alembic is used to generate migration files from SQLModel files. The initial migration should be done manually. Document the command to migrate DB.

## Tests

Implemented automated unit tests as specified for each component and service above. The tests should live in `tests/` directory and mimic the `app/` directory structure inside.

## README.md

Finally, a README.md should be defined for installation and setup instructions. AI_USAGE.md will be manually defined later.

Some data that should be present in the README.md:

How to seed the database: Load alembic migration, and run `parse_graph --file-path=samples/good/sample_graph_1.xml`