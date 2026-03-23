
-- Proposed SQL schema. Modeled in SQLModels in app/models.py

CREATE TABLE graph (
    -- primary key of the graph
    id VARCHAR(32) NOT NULL,
    -- name of the graph
    name TEXT NOT NULL,
    -- timestamp when row was created
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    -- define id attribute as the primary key
    PRIMARY KEY (id)
);

CREATE TABLE node (
    -- primary key of the node (composite)
    id VARCHAR(32) NOT NULL, 
    -- primary key of the node (composite)
    graph_id VARCHAR(32) NOT NULL, 
    -- name of the node
    name TEXT NOT NULL, 
    -- timestamp when row was created
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    -- define id and graph_id attributes as a composite primary key
    -- enforces that a node id is unique per graph (multiple graphs can have node with id "a" or "b")
    PRIMARY KEY (id, graph_id), 
    -- foreign key to a graph
    FOREIGN KEY(graph_id) REFERENCES graph (id)
);

-- create index on foreign key to a graph
CREATE INDEX idx_node_graph_id ON node (graph_id);

CREATE TABLE edge (
    -- primary key of the edge (composite)
    id VARCHAR(32) NOT NULL, 
    -- primary key of the edge (composite)
    graph_id VARCHAR(32) NOT NULL, 
    -- relationship to a previous node (composite)
    from_node_id VARCHAR(32) NOT NULL, 
    -- relationship to a next node (composite)
    to_node_id VARCHAR(32) NOT NULL, 
    -- weight of the edge
    cost NUMERIC, 
    -- timestamp when row was created
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    -- define id and graph_id attributes as a composite primary key
    -- enforces that a edge is unique per graph
    -- enfocess that you cannot add the same edge twice
    PRIMARY KEY (id, graph_id),
    -- foreign key to a graph
    FOREIGN KEY(graph_id) REFERENCES graph (id), 
    -- composite foreign keys to previous and next nodes
    FOREIGN KEY(from_node_id, graph_id) REFERENCES node (id, graph_id), 
    FOREIGN KEY(to_node_id, graph_id) REFERENCES node (id, graph_id)
);

-- create index on foreign key to a graph
CREATE INDEX idx_edge_graph_id ON edge (graph_id);

-- create indexes on composite foreign key to previous and next nodes, for faster traversal when finding cycles.
-- note: must be added manually, SQLModels do not create these for some reason (unresolved issue).
CREATE INDEX idx_edge_from_node_id ON edge (from_node_id, graph_id);
CREATE INDEX idx_edge_to_node_id ON edge (to_node_id, graph_id);
