## ADDED Requirements

### Requirement: Semantic memory search
The system SHALL support searching historical memories by semantic similarity using vector embeddings.

#### Scenario: Search by natural language query
- **WHEN** the user asks "我之前提到的数据库密码是什么？"
- **THEN** the system SHALL retrieve relevant messages containing the password information

#### Scenario: Return top-k most relevant results
- **WHEN** searching memories with top_k=3 parameter
- **THEN** the system SHALL return exactly 3 most semantically similar memory items

#### Scenario: Filter by session
- **WHEN** searching memories within a specific session_id
- **THEN** the system SHALL only return results from that session

### Requirement: Context augmentation
The system SHALL automatically augment LLM context with semantically relevant historical memories.

#### Scenario: Query-related memory retrieval
- **WHEN** processing a user query
- **THEN** the system SHALL search for related memories and include top 2 in the LLM context

#### Scenario: Relevance threshold filtering
- **WHEN** retrieved memories have similarity score < 0.6
- **THEN** the system SHALL exclude them from context augmentation

### Requirement: Memory result formatting
The system SHALL format retrieved memories appropriately for LLM consumption.

#### Scenario: Format as context messages
- **WHEN** memories are retrieved for context augmentation
- **THEN** the system SHALL format them as system messages with clear attribution

#### Scenario: Include timestamp and topic info
- **WHEN** returning search results
- **THEN** each result SHALL include original timestamp and topic tag
