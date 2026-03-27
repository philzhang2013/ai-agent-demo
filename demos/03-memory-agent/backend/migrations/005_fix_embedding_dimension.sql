-- ============================================
-- 修复向量维度：从 1536 改为 2048 (智谱 embedding-3)
-- ============================================

-- 注意：pgvector 的 ivfflat/hnsw 索引都有 2000 维限制
-- 智谱 embedding-3 是 2048 维，超过限制
-- 解决方案：不创建向量索引，使用全表扫描进行相似度计算

-- 1. 修改 messages 表的 embedding 字段维度
DROP INDEX IF EXISTS idx_messages_embedding;

ALTER TABLE messages
DROP COLUMN IF EXISTS embedding;

ALTER TABLE messages
ADD COLUMN embedding VECTOR(2048);

-- 不创建 ivfflat/hnsw 索引（因为 2048 > 2000 维限制）
-- 如需优化性能，可考虑：
--   1. 使用其他向量数据库（如 ChromaDB）
--   2. 截取向量到 2000 维
--   3. 对向量进行降维处理

-- 2. 修改 memory_segments 表的 embedding 字段维度
DROP INDEX IF EXISTS idx_segments_embedding;

ALTER TABLE memory_segments
DROP COLUMN IF EXISTS embedding;

ALTER TABLE memory_segments
ADD COLUMN embedding VECTOR(2048);

-- 3. 记录迁移信息
COMMENT ON COLUMN messages.embedding IS '消息向量嵌入 (2048维，智谱embedding-3)';
COMMENT ON COLUMN memory_segments.embedding IS '主题段向量嵌入 (2048维，智谱embedding-3)';
