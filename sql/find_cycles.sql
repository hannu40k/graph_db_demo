
-- A query to find cycles in a given directed graph, including self-loops and
-- all rotations of a cycle (the different order of traversed nodes you would
-- get if you started traversing the same cycle from a different node).

WITH RECURSIVE
-- A helper table to join and keep only to a particular graph in the database.
target_graph(graph_id) AS (
    VALUES ('cycle_graph_1'::text) -- Modify the string to target a particular graph id.
),
-- The main result set built using a recursive search. Does not find self-loops (handled
-- as a special case after recursive traversal).
traversal (start_node, current_node, path) AS (
    -- Anchor nodes, one row per edge.
    SELECT
        e.from_node_id                                        AS start_node,
        e.to_node_id                                          AS current_node,
        ARRAY[e.from_node_id::varchar, e.to_node_id::varchar] AS path -- Visited nodes
    FROM edge e
    JOIN target_graph t ON e.graph_id = t.graph_id -- JOIN: Keep within target graph.
    WHERE e.from_node_id <> e.to_node_id           -- Exclude self-loops.

    UNION ALL

    -- Recursively traverse the graph.
    SELECT
        tr.start_node           AS start_node,
        e.to_node_id            AS current_node,
        tr.path || e.to_node_id AS path -- Add current node to path, then move to next node.
    FROM traversal tr
    JOIN edge e ON e.from_node_id = tr.current_node
    JOIN target_graph t ON e.graph_id = t.graph_id -- JOIN: Keep within target graph.
    WHERE NOT e.to_node_id = ANY(tr.path)          -- Next hop is already encountered, do not continue further for this path.
)

-- Select the paths where a cycle was detected.
-- DISTINCT drops duplicate paths, in case any were produced.
SELECT DISTINCT tr.path || tr.start_node AS cycle_path -- Add the closing hop of the cycle to the path (returning to starting node).
FROM traversal tr
-- Join to find the edge that connects the current end of the path (tr.current_node) back to the start node. Any rows in traversal that don't have this edge are dropped.
-- The resulting tr.path is missing the closing hop, which is added in the SELECT above. The JOIN is effectively a filter, only rows that can match the JOIN are kept.
JOIN edge e
  ON e.from_node_id = tr.current_node
  AND e.to_node_id   = tr.start_node

-- Handle self-loops as a special case with a quick search, instead of
-- keeping them inside the recursive search.
UNION ALL

SELECT ARRAY[e.from_node_id::varchar, e.to_node_id::varchar] AS cycle_path
FROM edge e
JOIN target_graph t ON e.graph_id = t.graph_id -- JOIN: Keep within target graph.
WHERE e.from_node_id = e.to_node_id            -- Self-loops only.

ORDER BY cycle_path;
