-- =============================================================================
-- insert_graph_with_cycles_2.sql
-- Seed: cycle_graph_2 — mixed acyclic and cyclic subgraphs.
--
-- Graph structure:
--   Acyclic subgraph:  X → Y → Z
--   Cyclic subgraph:   P → Q → R → P
--   Cross-edge:        Y → P   (connects the two subgraphs)
--
-- The detect_cycles query should report the P→Q→R→P cycle and produce
-- no false positives for the acyclic X→Y→Z path.
--
-- Safe to re-run: INSERT ... ON CONFLICT DO NOTHING makes it idempotent.
-- =============================================================================

INSERT INTO graph (id, name)
VALUES ('cycle_graph_2', 'Cycle Graph 2 – mixed acyclic + cyclic subgraphs')
ON CONFLICT (id) DO NOTHING;

INSERT INTO node (id, graph_id, name) VALUES
  ('X', 'cycle_graph_2', 'Node X'),
  ('Y', 'cycle_graph_2', 'Node Y'),
  ('Z', 'cycle_graph_2', 'Node Z'),
  ('P', 'cycle_graph_2', 'Node P'),
  ('Q', 'cycle_graph_2', 'Node Q'),
  ('R', 'cycle_graph_2', 'Node R')
ON CONFLICT (id, graph_id) DO NOTHING;

-- 6 edges total: 2 acyclic, 3 cyclic, 1 cross-edge.
INSERT INTO edge (id, graph_id, from_node_id, to_node_id, cost) VALUES
  -- Acyclic subgraph (X → Y → Z)
  ('e1', 'cycle_graph_2', 'X', 'Y', 2.0),   -- X → Y
  ('e2', 'cycle_graph_2', 'Y', 'Z', 3.0),   -- Y → Z

  -- Cross-edge connecting the two subgraphs
  ('e3', 'cycle_graph_2', 'Y', 'P', 1.0),   -- Y → P

  -- Cyclic subgraph (P → Q → R → P)
  ('e4', 'cycle_graph_2', 'P', 'Q', 1.0),   -- P → Q
  ('e5', 'cycle_graph_2', 'Q', 'R', 1.0),   -- Q → R
  ('e6', 'cycle_graph_2', 'R', 'P', 1.0)    -- R → P  (closes the cycle)
ON CONFLICT (id, graph_id) DO NOTHING;
