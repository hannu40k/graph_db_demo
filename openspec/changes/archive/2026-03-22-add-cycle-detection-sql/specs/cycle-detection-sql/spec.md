## ADDED Requirements

### Requirement: Cycle detection SQL script
A file `sql/detect_cycles.sql` MUST exist containing a raw SQL query (SQL99 `WITH RECURSIVE`)
that detects all cycles in a **single** directed graph stored in the `edge` table.

The target graph is selected by a `graph_id` value hardcoded directly in the script.
To analyse a different graph, the operator edits that value and re-runs the script.

The query MUST:
- Operate against the schema defined in `app/models.py` (`graph`, `node`, `edge` tables)
- Filter all table access by the hardcoded `graph_id` so only one graph is examined per run
- Return `cycle_path` (an array of node IDs) for each detected cycle
- Correctly detect simple cycles (A→B→C→A), self-loops (A→A), and cycles within larger mixed graphs
- Produce no output when the targeted graph contains no cycles
- Guard against infinite recursion by terminating once a cycle is detected in the current path

#### Scenario: Simple 3-node cycle detected
Given the `edge` table contains edges A→B, B→C, C→A for `graph_id = 'cycle_graph_1'`
And the script has `graph_id` hardcoded to `'cycle_graph_1'`
When `sql/detect_cycles.sql` is executed
Then at least one result row is returned
And the `cycle_path` column contains the node IDs that form the cycle

#### Scenario: Self-loop detected
Given the `edge` table contains a self-loop edge D→D for `graph_id = 'cycle_graph_1'`
And the script has `graph_id` hardcoded to `'cycle_graph_1'`
When `sql/detect_cycles.sql` is executed
Then a result row for that self-loop is included in the output

#### Scenario: Acyclic graph produces no output
Given graph `g1` (sample graph 1) contains no cycles
And the script has `graph_id` hardcoded to `'g1'`
When `sql/detect_cycles.sql` is executed
Then zero rows are returned

#### Scenario: Mixed graph — only cyclic subgraph is reported
Given `cycle_graph_2` has an acyclic subgraph X→Y→Z and a cyclic subgraph P→Q→R→P
And the script has `graph_id` hardcoded to `'cycle_graph_2'`
When `sql/detect_cycles.sql` is executed
Then at least one result row is returned
And the `cycle_path` reflects the cyclic subgraph (P, Q, R, or equivalent)

#### Scenario: Complex graph — multiple distinct cycles reported
Given `cycle_graph_3` has 10 nodes and 20–30 edges with at least 4 distinct directed cycles
And the script has `graph_id` hardcoded to `'cycle_graph_3'`
When `sql/detect_cycles.sql` is executed
Then at least 4 result rows are returned
And each returned `cycle_path` represents a distinct cycle in the graph

### Requirement: Seed script — cycle_graph_1
A file `sql/insert_graph_with_cycles_1.sql` MUST exist that inserts a graph
with id `cycle_graph_1` containing at least one 3-node directed cycle and one self-loop
into the `graph`, `node`, and `edge` tables.

The script MUST be idempotent (`INSERT ... ON CONFLICT DO NOTHING`).

#### Scenario: Script runs against clean DB
Given the `graphdb` or `graphdb_test` database has the schema applied
When `sql/insert_graph_with_cycles_1.sql` is executed
Then `SELECT * FROM graph WHERE id = 'cycle_graph_1'` returns exactly one row
And the inserted edges include at least one directed cycle

#### Scenario: Script is idempotent
Given `sql/insert_graph_with_cycles_1.sql` has already been run once
When it is run a second time
Then no error is raised and no duplicate rows are created

### Requirement: Seed script — cycle_graph_2
A file `sql/insert_graph_with_cycles_2.sql` MUST exist that inserts a graph
with id `cycle_graph_2` containing both acyclic and cyclic subgraphs connected by at least
one cross-edge into the `graph`, `node`, and `edge` tables.

The script MUST be idempotent (`INSERT ... ON CONFLICT DO NOTHING`).

#### Scenario: Script runs against clean DB
Given the schema is applied
When `sql/insert_graph_with_cycles_2.sql` is executed
Then `SELECT * FROM graph WHERE id = 'cycle_graph_2'` returns exactly one row
And the graph contains at least one cycle and at least one node not part of any cycle

#### Scenario: Script is idempotent
Given `sql/insert_graph_with_cycles_2.sql` has already been run once
When it is run a second time
Then no error is raised and no duplicate rows are created

### Requirement: Seed script — cycle_graph_3
A file `sql/insert_graph_with_cycles_3.sql` MUST exist that inserts a graph
with id `cycle_graph_3` containing exactly 10 nodes (n1–n10), between 20 and 30 directed
edges, and at least 4 distinct directed cycles into the `graph`, `node`, and `edge` tables.

The script MUST be idempotent (`INSERT ... ON CONFLICT DO NOTHING`).

#### Scenario: Script runs against clean DB
Given the schema is applied
When `sql/insert_graph_with_cycles_3.sql` is executed
Then `SELECT count(*) FROM node WHERE graph_id = 'cycle_graph_3'` returns 10
And `SELECT count(*) FROM edge WHERE graph_id = 'cycle_graph_3'` returns a value between 20 and 30
And the graph contains at least 4 distinct directed cycles

#### Scenario: Script is idempotent
Given `sql/insert_graph_with_cycles_3.sql` has already been run once
When it is run a second time
Then no error is raised and no duplicate rows are created
