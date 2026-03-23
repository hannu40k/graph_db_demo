# Proposal: add-latest-graph-query

## Summary
Add a `POST /query` endpoint (no graph ID in path) that executes queries against the most recently inserted graph in the database. This complements the existing `POST /query/{graph_id}` endpoint and satisfies the original spec's intent of supporting a bare `/query` path.

## Motivation
The original assignment spec describes `POST /query` as the query endpoint. The implementation correctly extended this to `POST /query/{graph_id}` to allow targeting specific graphs. However, the bare `POST /query` route is missing. A client that does not know (or care about) a specific graph ID should be able to query the latest graph that was loaded into the database.

## Scope
- Add `POST /query` route to `app/main.py`
- Add `get_latest_graph` method to `GraphService`
- Return HTTP 404 when no graphs exist in the database
- All existing `POST /query/{graph_id}` behaviour is unchanged

## Out of Scope
- Changing any existing endpoint behaviour
- Pagination or graph listing
- Authentication
