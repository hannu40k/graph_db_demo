## MODIFIED Requirements
### Requirement: API Request Format
The system SHALL accept requests with a `queries` array where each item contains **exactly one** of: a `paths` key or a `cheapest` key. Each key holds an object with `start` and `end` string fields identifying node IDs. A query item with both keys set, or with neither key set, SHALL be rejected with HTTP 422. The API schema (OpenAPI) SHALL reflect this constraint so that generated examples do not show both keys simultaneously.

#### Scenario: Mixed query types in single request
- **WHEN** a request contains both `paths` and `cheapest` query items (one per item)
- **THEN** all queries are processed and answered in order

#### Scenario: Query item with both paths and cheapest rejected
- **WHEN** a request contains a query item with both `paths` and `cheapest` keys set
- **THEN** the system SHALL return HTTP 422 with a descriptive validation error

#### Scenario: Query item with neither key rejected
- **WHEN** a request contains a query item with neither `paths` nor `cheapest` key set
- **THEN** the system SHALL return HTTP 422 with a descriptive validation error
