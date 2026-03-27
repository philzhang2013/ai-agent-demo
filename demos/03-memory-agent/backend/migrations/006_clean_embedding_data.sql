-- ============================================-- 清理旧向量数据并确保维度正确 (006_clean_embedding_data)-- ============================================
-- 问题：数据库中仍存在 1536 维的旧数据
-- 解决：清空所有 embedding 数据，让系统重新生成 2048 维向量

-- 1. 清空 messages 表的 embedding 列（智谱 embedding-3 使用 2048 维）
UPDATE messages SET embedding = NULL;

-- 2. 清空 memory_segments 表的 embedding 列
UPDATE memory_segments SET embedding = NULL;

-- 3. 记录清理信息
COMMENT ON COLUMN messages.embedding IS '消息向量嵌入 (2048维，智谱embedding-3) - 2026-03-27 清理旧数据';
COMMENT ON COLUMN memory_segments.embedding IS '主题段向量嵌入 (2048维，智谱embedding-3) - 2026-03-27 清理旧数据';
