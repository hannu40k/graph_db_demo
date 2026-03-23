-- =============================================================================
-- insert_graph_with_cycles_1.sql
-- Seed: cycle_graph_1 — minimal 3-node directed cycle plus a self-loop.
--
-- Graph structure:
--   A → B → C → A   (simple 3-node cycle)
--   D → D            (self-loop — trivially cyclic)
--
-- Safe to re-run: INSERT ... ON CONFLICT DO NOTHING makes it idempotent.
-- =============================================================================

INSERT INTO graph (id, name)
VALUES ('cycle_graph_1', 'Cycle Graph 1 – simple cycle and self-loop')
ON CONFLICT (id) DO NOTHING;

INSERT INTO node (id, graph_id, name) VALUES
  ('A', 'cycle_graph_1', 'Node A'),
  ('B', 'cycle_graph_1', 'Node B'),
  ('C', 'cycle_graph_1', 'Node C'),
  ('D', 'cycle_graph_1', 'Node D')
ON CONFLICT (id, graph_id) DO NOTHING;

-- Edges forming the 3-node cycle A → B → C → A, plus self-loop D → D.
INSERT INTO edge (id, graph_id, from_node_id, to_node_id, cost) VALUES
  ('e1', 'cycle_graph_1', 'A', 'B', 1.0),   -- A → B
  ('e2', 'cycle_graph_1', 'B', 'C', 1.0),   -- B → C
  ('e3', 'cycle_graph_1', 'C', 'A', 1.0),   -- C → A  (closes the cycle)
  ('e4', 'cycle_graph_1', 'D', 'D', 0.0)    -- D → D  (self-loop)
ON CONFLICT (id, graph_id) DO NOTHING;
