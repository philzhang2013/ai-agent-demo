## ADDED Requirements

### Requirement: Vector embedding generation
The system SHALL generate vector embeddings for text content using an embedding model.

#### Scenario: Generate message embedding
- **WHEN** a new message is stored
- **THEN** the system SHALL generate a 1536-dimensional vector embedding

#### Scenario: Generate summary embedding
- **WHEN** a memory segment summary is created
- **THEN** the system SHALL generate and store its vector embedding

### Requirement: pgvector storage
The system SHALL store vector embeddings in PostgreSQL using the pgvector extension.

#### Scenario: Store message with embedding
- **WHEN** storing a message with importance score >= 0.5
- **THEN** the system SHALL store both content and its vector embedding in messages table

#### Scenario: Store segment summary embedding
- **WHEN** creating or updating a memory segment
- **THEN** the system SHALL store the summary's vector embedding in memory_segments table

### Requirement: Similarity search with pgvector
The system SHALL perform cosine similarity searches using pgvector.

#### Scenario: Search messages by vector similarity
- **WHEN** searching with a query vector
- **THEN** the system SHALL return messages ordered by cosine similarity using the ivfflat index

#### Scenario: Search segments by vector similarity
- **WHEN** searching memory segments
- **THEN** the system SHALL use pgvector's vector_cosine_ops operator for efficient search

### Requirement: Index management
The system SHALL maintain efficient vector indexes for fast similarity search.

#### Scenario: Create vector indexes
- **WHEN** initializing the database
- **THEN** the system SHALL create ivfflat indexes on messages.embedding and memory_segments.embedding

#### Scenario: Handle pgvector extension
- **WHEN** connecting to database
- **THEN** the system SHALL verify pgvector extension is installed and enabled
