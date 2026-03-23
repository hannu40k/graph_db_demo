# Change: Add cycle detection SQL scripts

## Why
The application stores directed graphs in PostgreSQL but provides no tooling to inspect
whether a stored graph contains cycles — a fundamental property for debugging and validation.
This change adds a raw-SQL recursive CTE script plus three seed graphs so operators can
detect cycles directly at the database level without running application code.

## What Changes
- New file `sql/detect_cycles.sql` — recursive CTE that detects all cycles in a single graph
- New file `sql/insert_graph_with_cycles_1.sql` — seed: minimal 3-node cycle + self-loop
- New file `sql/insert_graph_with_cycles_2.sql` — seed: mixed acyclic + cyclic subgraphs
- New file `sql/insert_graph_with_cycles_3.sql` — seed: 10 nodes, 20–30 edges, ≥4 cycles

## Impact
- Affected specs: `cycle-detection-sql` (new capability)
- Affected code: new `sql/` directory; no changes to existing application code

---

## Algorithm: recursive CTE cycle detection

The `detect_cycles.sql` query uses a `WITH RECURSIVE` CTE, which is standard SQL99 and
fully supported by PostgreSQL.

**Approach:**
1. **Base case** — seed one row per edge in the graph, recording the `start_node` and a
   `path` array of visited nodes so far (`[from_node_id]`).
2. **Recursive step** — join to the next outgoing edge. If the `to_node_id` is already
   in `path`, mark `cycle_detected = TRUE` and stop recursing (the `WHERE NOT cycle_detected`
   guard prevents runaway recursion).
3. **Result** — `SELECT DISTINCT graph_id, path` from rows where `cycle_detected = TRUE`,
   giving one representative cycle path per detected cycle.

**Self-loops:** each self-loop (`from_node_id = to_node_id`) is itself a trivially detected
cycle — the very first step detects it before recursion begins.

**Output columns:**
- `cycle_path TEXT[]` — the node IDs that form the cycle (the path that triggered detection)

## Seed scripts

### `insert_graph_with_cycles_1.sql`
A minimal 3-node graph `cycle_graph_1`:
- Nodes: A, B, C
- Edges: A→B, B→C, C→A (forms a single cycle)
- Also includes a self-loop D→D for completeness

### `insert_graph_with_cycles_2.sql`
A larger graph `cycle_graph_2` with mixed structure:
- One subgraph that is acyclic (X→Y→Z)
- One subgraph that has a cycle (P→Q→R→P)
- One additional cross-edge (Y→P) so the two components are connected

### `insert_graph_with_cycles_3.sql`
A stress-test graph `cycle_graph_3` designed to exercise the query on a denser graph:
- 10 nodes: n1–n10
- 20–30 directed edges with varying costs
- At least 4 distinct directed cycles, for example:
  - n1→n2→n3→n1 (3-node)
  - n4→n5→n6→n7→n4 (4-node)
  - n2→n4→n8→n2 (3-node crossing the first two cycles)
  - n5→n9→n10→n5 (3-node)
- Additional edges between cycles to create a densely connected graph

All three scripts are `INSERT ... ON CONFLICT DO NOTHING` so they are safe to re-run.

## Performance implications on large graphs

The recursive CTE performs a depth-first traversal of the entire reachable subgraph for
every starting edge. In the worst case (dense graph, long cycles) this yields O(V × E)
row generation before the cycle guard kicks in. Key considerations:

- **Index requirement**: `edge(graph_id, from_node_id)` should be indexed for the recursive
  join to scale. Without it, each recursive step performs a full table scan on `edge`.
- **Memory**: PostgreSQL materialises the CTE working table in memory. A graph with
  thousands of edges can produce millions of intermediate rows; consider `work_mem` tuning.
- **DISTINCT deduplication**: the final `SELECT DISTINCT` adds a sort/hash step proportional
  to the number of detected cycle paths, which is usually small.
- **Practical ceiling**: the query is designed for diagnostic/manual use, not real-time
  API calls. For graphs beyond ~500 nodes / 2 000 edges, prefer the in-process networkx
  `simple_cycles()` algorithm already available in the service layer.
- **Termination guarantee**: the `WHERE NOT cycle_detected` guard ensures the CTE always
  terminates — once a back-edge is found for a given path, that branch stops expanding.
