## MODIFIED Requirements
### Requirement: API Response Format
The system SHALL return responses with an `answers` array where each item contains **exactly one** of: a `paths` key (with `from`, `to`, `paths` fields) or a `cheapest` key (with `from`, `to`, `path` fields). The `from`/`to` fields echo the requested start/end nodes. Keys that are absent from the query result SHALL be **omitted** from the answer item — they MUST NOT appear as `null`.

#### Scenario: Response matches request order
- **WHEN** three queries are sent (paths a->e, cheapest a->e, cheapest a->h)
- **THEN** three answers are returned in the same order with matching query types

#### Scenario: Paths-only answer omits cheapest key
- **WHEN** a query item contains only a `paths` query
- **THEN** the corresponding answer item contains a `paths` key and NO `cheapest` key (not even `null`)

#### Scenario: Cheapest-only answer omits paths key
- **WHEN** a query item contains only a `cheapest` query
- **THEN** the corresponding answer item contains a `cheapest` key and NO `paths` key (not even `null`)
