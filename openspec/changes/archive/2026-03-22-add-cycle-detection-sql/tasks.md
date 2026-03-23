# Tasks: add-cycle-detection-sql

## Ordered Work Items

1. **Create `sql/` directory**
   - Validation: `ls sql/` shows the directory
   - [x] Done

2. **Write `sql/insert_graph_with_cycles_1.sql`**
   - INSERT `cycle_graph_1`: 3-node cycle (A→B→C→A) plus self-loop (D→D)
   - Use `INSERT ... ON CONFLICT DO NOTHING` so the script is idempotent
   - Validation: run against the live DB; `SELECT * FROM graph WHERE id = 'cycle_graph_1'` returns one row
   - [x] Done

3. **Write `sql/insert_graph_with_cycles_2.sql`**
   - INSERT `cycle_graph_2`: mixed acyclic (X→Y→Z) and cyclic (P→Q→R→P) subgraphs, connected by Y→P
   - Use `INSERT ... ON CONFLICT DO NOTHING`
   - Validation: run against the live DB; `SELECT count(*) FROM edge WHERE graph_id = 'cycle_graph_2'` returns 6
   - [x] Done

4. **Write `sql/insert_graph_with_cycles_3.sql`**
   - INSERT `cycle_graph_3`: 10 nodes (n1–n10), 26 directed edges, 4 distinct cycles
   - Use `INSERT ... ON CONFLICT DO NOTHING`
   - Validation: run against the live DB; `SELECT count(*) FROM node WHERE graph_id = 'cycle_graph_3'` returns 10; `SELECT count(*) FROM edge WHERE graph_id = 'cycle_graph_3'` returns 26
   - [x] Done

5. **Write `sql/detect_cycles.sql`**
   - Implement the recursive CTE cycle-detection query targeting the `edge` table for a **single** graph
   - The `graph_id` to analyse is hardcoded in the script; editing that value and re-running targets a different graph
   - Output column: `cycle_path` (TEXT array of node IDs per detected cycle)
   - Guard against runaway recursion with `WHERE NOT cycle_detected`
   - Validation (run the script once per target graph by editing the hardcoded `graph_id`):
     - Set `graph_id = 'cycle_graph_1'` → at least one row returned including the self-loop
     - Set `graph_id = 'cycle_graph_2'` → at least one row returned reflecting the P→Q→R→P cycle
     - Set `graph_id = 'cycle_graph_3'` → at least 4 distinct `cycle_path` values returned
     - Set `graph_id = 'g1'` → zero rows returned (no false positives on an acyclic graph)
   - [x] Done

## Dependencies
- Task 1 must complete before tasks 2–5
- Tasks 2, 3, and 4 are parallelisable
- Task 5 is independent of tasks 2–4 (query correctness is validated against the seeded data)

## Verification
```bash
# Load seed data
psql $DATABASE_URL -f sql/insert_graph_with_cycles_1.sql
psql $DATABASE_URL -f sql/insert_graph_with_cycles_2.sql
psql $DATABASE_URL -f sql/insert_graph_with_cycles_3.sql

# Edit the hardcoded graph_id in sql/detect_cycles.sql, then run:

# Cyclic graphs — each should return rows
# (set graph_id = 'cycle_graph_1' in the script)
psql $DATABASE_URL -f sql/detect_cycles.sql

# (set graph_id = 'cycle_graph_2' in the script)
psql $DATABASE_URL -f sql/detect_cycles.sql

# (set graph_id = 'cycle_graph_3' in the script — expect ≥ 4 rows)
psql $DATABASE_URL -f sql/detect_cycles.sql

# Acyclic graph — must return zero rows
# (set graph_id = 'g1' in the script)
psql $DATABASE_URL -f sql/detect_cycles.sql
```
