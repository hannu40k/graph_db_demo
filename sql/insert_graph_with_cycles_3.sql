-- =============================================================================
-- insert_graph_with_cycles_3.sql
-- Seed: cycle_graph_3 — dense graph: 10 nodes, 26 edges, 4 distinct cycles.
--
-- Nodes: n1 – n10
--
-- The four distinct directed cycles are:
--   Cycle 1 (3-node):  n1 → n2 → n3 → n1
--   Cycle 2 (4-node):  n4 → n5 → n6 → n7 → n4
--   Cycle 3 (3-node):  n2 → n4 → n8 → n2   (crosses cycles 1 and 2)
--   Cycle 4 (3-node):  n5 → n9 → n10 → n5
--
-- Additional cross-edges connect the four cycle clusters, making the graph
-- densely connected (26 edges total — within the 20–30 target range).
--
-- Safe to re-run: INSERT ... ON CONFLICT DO NOTHING makes it idempotent.
-- =============================================================================

INSERT INTO graph (id, name)
VALUES ('cycle_graph_3', 'Cycle Graph 3 – 10 nodes, 26 edges, 4 distinct cycles')
ON CONFLICT (id) DO NOTHING;

INSERT INTO node (id, graph_id, name) VALUES
  ('n1',  'cycle_graph_3', 'Node 1'),
  ('n2',  'cycle_graph_3', 'Node 2'),
  ('n3',  'cycle_graph_3', 'Node 3'),
  ('n4',  'cycle_graph_3', 'Node 4'),
  ('n5',  'cycle_graph_3', 'Node 5'),
  ('n6',  'cycle_graph_3', 'Node 6'),
  ('n7',  'cycle_graph_3', 'Node 7'),
  ('n8',  'cycle_graph_3', 'Node 8'),
  ('n9',  'cycle_graph_3', 'Node 9'),
  ('n10', 'cycle_graph_3', 'Node 10')
ON CONFLICT (id, graph_id) DO NOTHING;

INSERT INTO edge (id, graph_id, from_node_id, to_node_id, cost) VALUES
  -- ---------------------------------------------------------------
  -- Cycle 1: n1 → n2 → n3 → n1  (3-node cycle)
  -- ---------------------------------------------------------------
  ('e01', 'cycle_graph_3', 'n1', 'n2',  1.0),
  ('e02', 'cycle_graph_3', 'n2', 'n3',  1.0),
  ('e03', 'cycle_graph_3', 'n3', 'n1',  1.0),   -- closes cycle 1

  -- ---------------------------------------------------------------
  -- Cycle 2: n4 → n5 → n6 → n7 → n4  (4-node cycle)
  -- ---------------------------------------------------------------
  ('e04', 'cycle_graph_3', 'n4', 'n5',  2.0),
  ('e05', 'cycle_graph_3', 'n5', 'n6',  2.0),
  ('e06', 'cycle_graph_3', 'n6', 'n7',  2.0),
  ('e07', 'cycle_graph_3', 'n7', 'n4',  2.0),   -- closes cycle 2

  -- ---------------------------------------------------------------
  -- Cycle 3: n2 → n4 → n8 → n2  (3-node, crosses cycles 1 and 2)
  -- ---------------------------------------------------------------
  ('e08', 'cycle_graph_3', 'n2', 'n4',  3.0),
  ('e09', 'cycle_graph_3', 'n4', 'n8',  3.0),
  ('e10', 'cycle_graph_3', 'n8', 'n2',  3.0),   -- closes cycle 3

  -- ---------------------------------------------------------------
  -- Cycle 4: n5 → n9 → n10 → n5  (3-node)
  -- ---------------------------------------------------------------
  ('e11', 'cycle_graph_3', 'n5', 'n9',  4.0),
  ('e12', 'cycle_graph_3', 'n9', 'n10', 4.0),
  ('e13', 'cycle_graph_3', 'n10', 'n5', 4.0),  -- closes cycle 4

  -- ---------------------------------------------------------------
  -- Cross-edges connecting the cycle clusters (13 additional edges)
  -- These bring the total to 26 edges and increase graph density.
  -- ---------------------------------------------------------------
  ('e14', 'cycle_graph_3', 'n1', 'n4',  5.0),  -- cluster 1 → cluster 2
  ('e15', 'cycle_graph_3', 'n2', 'n5',  5.0),
  ('e16', 'cycle_graph_3', 'n3', 'n6',  5.0),
  ('e17', 'cycle_graph_3', 'n4', 'n1',  5.0),  -- cluster 2 → cluster 1
  ('e18', 'cycle_graph_3', 'n5', 'n2',  5.0),
  ('e19', 'cycle_graph_3', 'n6', 'n3',  5.0),
  ('e20', 'cycle_graph_3', 'n7', 'n8',  6.0),  -- cluster 2 → cluster 3
  ('e21', 'cycle_graph_3', 'n8', 'n9',  6.0),  -- cluster 3 → cluster 4
  ('e22', 'cycle_graph_3', 'n9', 'n1',  6.0),  -- cluster 4 → cluster 1
  ('e23', 'cycle_graph_3', 'n10', 'n4', 6.0),  -- cluster 4 → cluster 2
  ('e24', 'cycle_graph_3', 'n1', 'n7',  7.0),
  ('e25', 'cycle_graph_3', 'n3', 'n8',  7.0),
  ('e26', 'cycle_graph_3', 'n6', 'n10', 7.0)
ON CONFLICT (id, graph_id) DO NOTHING;
