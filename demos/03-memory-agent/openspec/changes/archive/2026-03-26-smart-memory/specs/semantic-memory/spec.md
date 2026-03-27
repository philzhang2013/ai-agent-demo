## ADDED Requirements

### Requirement: Message importance scoring
The system SHALL assign an importance score (0.0 to 1.0) to each incoming message based on semantic analysis.

#### Scenario: High importance message detected
- **WHEN** a user sends a message containing critical information like "我的数据库密码是 123456"
- **THEN** the system SHALL assign an importance score >= 0.8

#### Scenario: Low importance message detected
- **WHEN** a user sends a casual greeting like "你好" or "谢谢"
- **THEN** the system SHALL assign an importance score <= 0.3

#### Scenario: Medium importance message
- **WHEN** a user sends a general question like "Python 怎么安装？"
- **THEN** the system SHALL assign an importance score between 0.4 and 0.7

### Requirement: Adaptive summary triggering
The system SHALL generate or update memory summaries based on accumulated importance scores, not fixed message counts.

#### Scenario: Trigger summary by accumulated importance
- **WHEN** the sum of importance scores for unprocessed messages exceeds 2.0
- **THEN** the system SHALL trigger a summary generation

#### Scenario: Skip summary for low-importance batch
- **WHEN** 10 messages have accumulated but total importance score is < 1.0
- **THEN** the system SHALL NOT generate a summary yet

### Requirement: Topic segmentation
The system SHALL automatically detect topic boundaries and segment conversations into logical memory segments.

#### Scenario: Detect topic switch
- **WHEN** a conversation shifts from "讨论数据库设计" to "我们聊聊前端框架"
- **THEN** the system SHALL create a new memory segment for the new topic

#### Scenario: Maintain topic continuity
- **WHEN** consecutive messages discuss the same topic
- **THEN** the system SHALL keep them in the same memory segment

### Requirement: Segment-based summary generation
The system SHALL generate and maintain separate summaries for each topic segment.

#### Scenario: Generate segment summary
- **WHEN** a topic segment is created or updated with new messages
- **THEN** the system SHALL generate a concise summary of that segment

#### Scenario: Retrieve segment context
- **WHEN** building context for LLM inference
- **THEN** the system SHALL include relevant segment summaries based on current topic
