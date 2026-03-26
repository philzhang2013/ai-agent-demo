-- 创建记忆摘要表
CREATE TABLE memory_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,           -- 摘要内容
    message_count INTEGER NOT NULL,  -- 总结了多少条消息
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id)               -- 每个会话只有一个摘要
);

-- 创建索引
CREATE INDEX idx_memory_summaries_session ON memory_summaries(session_id);

-- 创建更新时间戳的触发器函数
CREATE OR REPLACE FUNCTION update_memory_summaries_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_update_memory_summaries_updated_at
    BEFORE UPDATE ON memory_summaries
    FOR EACH ROW
    EXECUTE FUNCTION update_memory_summaries_updated_at();
