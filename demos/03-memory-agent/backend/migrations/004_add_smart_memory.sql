-- ============================================
-- 智能记忆系统数据库迁移 (004_add_smart_memory)
-- ============================================
-- 注意：使用智谱 embedding-3，向量维度为 2048
-- pgvector 的 ivfflat/hnsw 索引有 2000 维限制，因此不创建向量索引

-- 1. 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 扩展 messages 表 - 新增智能记忆相关字段
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS importance_score FLOAT DEFAULT 0.5,
ADD COLUMN IF NOT EXISTS topic_tag VARCHAR(100),
ADD COLUMN IF NOT EXISTS embedding VECTOR(2048);  -- 智谱 embedding-3: 2048维

-- 3. 创建 messages 表索引（不包含向量索引，因维度超过 pgvector 限制）
CREATE INDEX IF NOT EXISTS idx_messages_importance ON messages(importance_score);
CREATE INDEX IF NOT EXISTS idx_messages_topic ON messages(topic_tag);
-- 注意：不创建 idx_messages_embedding，因为 2048 > 2000 (pgvector 索引限制)

-- 4. 创建 memory_segments 主题段表
CREATE TABLE IF NOT EXISTS memory_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    topic_name VARCHAR(200) NOT NULL DEFAULT '未命名主题',

    -- 段落边界（引用 messages 表）
    start_message_id UUID REFERENCES messages(id),
    end_message_id UUID REFERENCES messages(id),

    -- 摘要内容
    summary_content TEXT NOT NULL DEFAULT '',
    importance_score FLOAT DEFAULT 0.0,

    -- 向量表示（用于语义检索）- 智谱 embedding-3: 2048维
    embedding VECTOR(2048),

    -- 统计信息
    message_count INTEGER DEFAULT 0,
    total_importance FLOAT DEFAULT 0.0,

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 创建 memory_segments 表索引（不包含向量索引）
CREATE INDEX IF NOT EXISTS idx_segments_session ON memory_segments(session_id);
-- 注意：不创建 idx_segments_embedding，因为 2048 > 2000 (pgvector 索引限制)

-- 6. 创建更新时间戳触发器函数
CREATE OR REPLACE FUNCTION update_memory_segments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. 创建触发器
DROP TRIGGER IF EXISTS trigger_update_memory_segments_updated_at ON memory_segments;
CREATE TRIGGER trigger_update_memory_segments_updated_at
    BEFORE UPDATE ON memory_segments
    FOR EACH ROW
    EXECUTE FUNCTION update_memory_segments_updated_at();
