-- 添加会话标题字段
ALTER TABLE sessions
ADD COLUMN title VARCHAR(200) NOT NULL DEFAULT '新对话';

-- 创建优化索引（用于会话列表查询）
CREATE INDEX idx_sessions_user_updated
ON sessions(user_id, updated_at DESC);
