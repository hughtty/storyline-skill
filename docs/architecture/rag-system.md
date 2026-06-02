# Storyline Skill — RAG 检索系统设计

## 设计目标

让用户能用自然语言快速找到任何剧情内容、角色信息、世界观设定，而不需要手动翻阅文件。

## 检索场景

### 场景 1：延续创作时查找历史
```
用户："小智在上次数学课里是什么表现？"
系统：→ 检索 character_graph.json 中 小智 的 appearances
      → 过滤 subject=数学
      → 返回 ep01 中的角色弧光摘要
```

### 场景 2：查找可用角色
```
用户："需要一个谨慎聪明的角色"
系统：→ 语义检索 character chunks（性格字段）
      → 匹配 "谨慎" "聪明" → 小慧
      → 返回角色档案 + 可用性状态
```

### 场景 3：查找知识点关联剧情
```
用户："之前有没有用过'钥匙模式'的抓手？"
系统：→ 检索 knowledge_map.json（storyline_pattern）
      → 或语义检索 story_outline chunks（抓手描述）
      → 返回匹配的课时列表
```

### 场景 4：跨课时钩子追踪
```
用户："ep01 抛出的钩子在哪节课回收了？"
系统：→ 检索 episode_graph.json edges
      → 找到 from=ep01 的边
      → 返回关联课时 + 钩子回收说明
```

### 场景 5：对白复用/查找
```
用户："小智说过'让我来'吗？在哪？"
系统：→ 检索 node_scripts chunks（对白内容）
      → 精确匹配或语义相似
      → 返回课时 + 节点编号 + 上下文
```

## 检索分层架构

```
┌─────────────────────────────────────────────────────────┐
│  查询层（Query Layer）                                    │
│  ├── 查询分类器：判断查询类型（角色/剧情/对白/世界观）      │
│  └── 查询改写：将自然语言转化为结构化检索条件              │
├─────────────────────────────────────────────────────────┤
│  索引层（Index Layer）                                    │
│  ├── 结构化索引（JSON）：index.json, character_graph.json   │
│  │   └── 用于：精确匹配、范围查询、关系遍历                │
│  └── 语义索引（Chunks）：*.chunks.json                     │
│      └── 用于：语义相似、模糊匹配、概念关联                │
├─────────────────────────────────────────────────────────┤
│  存储层（Storage Layer）                                  │
│  ├── 内容文件：*.md                                       │
│  ├── 索引文件：*.json                                     │
│  └── 向量存储：*.chunks.json（embedding 向量）             │
└─────────────────────────────────────────────────────────┘
```

## 查询分类器

```python
# 伪代码示意
def classify_query(query: str) -> QueryType:
    if contains(query, ["角色", "谁", "人物", "性格"]):
        return QueryType.CHARACTER
    elif contains(query, ["课时", "课", "故事", "剧情", "知识点"]):
        return QueryType.EPISODE
    elif contains(query, ["对白", "台词", "说过", "说了"]):
        return QueryType.DIALOGUE
    elif contains(query, ["世界观", "场景", "地点", "背景"]):
        return QueryType.WORLDVIEW
    elif contains(query, ["关系", "联系", "关联", "上一课", "下一课"]):
        return QueryType.RELATION
    else:
        return QueryType.SEMANTIC  # 默认走语义检索
```

## 检索策略（按查询类型）

### CHARACTER 查询

```
输入："找一个适合数学课、性格勇敢的角色"

Step 1: 结构化过滤
  → character_graph.json
  → filter: subjects contains "数学"
  → candidates: [小智, ...]

Step 2: 语义排序
  → 检索 candidates 的性格 chunks
  → semantic match: "勇敢"
  → rank by similarity

Step 3: 返回
  → 角色名 + 档案摘要 + 出场历史 + 可用性
```

### EPISODE 查询

```
输入："三年级英语、关于时态的课时"

Step 1: 结构化过滤
  → index.json episodes
  → filter: grade="三年级" AND subject="英语"
  → candidates: [ep01, ep02, ...]

Step 2: 语义确认
  → 检索 candidates 的 story_outline chunks
  → semantic match: "时态"
  → rank by similarity

Step 3: 返回
  → 课时列表 + 一句话梗概 + 知识点匹配度
```

### DIALOGUE 查询

```
输入："小智说过'让我来'吗？"

Step 1: 结构化过滤
  → character_graph.json
  → 找到 小智 的所有 appearances
  → 获取对应 episode_ids

Step 2: 精确检索
  → 检索这些 episodes 的 node_scripts chunks
  → exact match: "让我来" OR semantic match: "我来" "让我"
  → 返回匹配片段 + 上下文
```

### RELATION 查询

```
输入："ep01 和哪些课时有关联？"

Step 1: 图遍历
  → episode_graph.json
  → 找到 node "ep01"
  → 遍历所有 edges (from=ep01 OR to=ep01)
  → 返回关联课时 + 关系类型 + 钩子说明
```

### SEMANTIC 查询

```
输入："找一个有反转的剧情"

Step 1: 全局语义检索
  → 检索所有 story_outline chunks
  → semantic match: "反转" "意外" "真相"
  → rank by similarity

Step 2: 返回
  → 匹配的课时 + 相关片段 + 相似度分数
```

## 语义分块策略（Chunking）

### 分块原则

1. **语义完整性**：每个 chunk 是一个完整的语义单元
2. **上下文保留**：chunk 包含必要的上下文信息
3. **可溯源**：每个 chunk 能追溯到原始文件和位置
4. **适度粒度**：不要太细（失去语义）也不要太粗（检索不精确）

### 各文件类型的分块方式

| 文件类型 | 分块方式 | Chunk 示例 |
|----------|----------|-----------|
| 角色档案 | 按字段分块 | {"type": "性格", "content": "勇敢但莽撞..."} |
| 故事梗概 | 按段落分块 | {"type": "第一幕", "content": "开场动画..."} |
| 教学节点 | 按节点分块 | {"type": "节点01", "content": "触发时机..."} |
| 分镜脚本 | 按镜头分块 | {"type": "镜头01", "content": "景别：全景..."} |
| 节点对白 | 按场景分块 | {"type": "节点01对白", "content": "小智：让我来..."} |
| 世界观 | 按章节分块 | {"type": "核心规则", "content": "魔法能量=语言能力..."} |

### Chunk 元数据

```json
{
  "id": "magic-english-academy/ep01/story-outline/02",
  "project_id": "magic-english-academy",
  "episode_id": "ep01",
  "file_path": "episodes/ep01/story_outline.md",
  "file_type": "story_outline",
  "chunk_type": "角色任务分配",
  "content": "小智：遭遇困境型，在魔法图书馆发现被封印的书...",
  "tags": ["小智", "主角", "魔法图书馆", "开场"],
  "created_at": "2024-06-01T10:00:00Z",
  "updated_at": "2024-06-01T10:00:00Z"
}
```

## Embedding 策略

由于当前系统基于本地文件，Embedding 可采用以下方案：

### 方案 A：本地 Embedding（推荐）

使用轻量级本地模型生成向量：
- **模型**：sentence-transformers/all-MiniLM-L6-v2（384维）
- **存储**：*.chunks.json 中直接存储向量
- **检索**：余弦相似度计算
- **优点**：完全离线，速度快
- **缺点**：向量占用存储空间

### 方案 B：关键词索引（轻量）

不生成 Embedding，而是构建倒排索引：
- **提取关键词**：从 chunks 中提取关键词
- **倒排索引**：keyword → [chunk_ids]
- **检索**：关键词匹配 + TF-IDF 排序
- **优点**：无需模型，极度轻量
- **缺点**：无法语义匹配

### 方案 C：混合方案（最佳）

结构化和语义结合：
- **结构化查询**（精确条件）→ JSON 索引
- **语义查询**（模糊概念）→ Embedding 检索
- **混合排序**：结构化过滤后，语义排序

## 索引维护机制

### 创建时
```
生成文件 → 解析内容 → 分块 → 生成 Embedding → 写入 chunks.json → 更新上级索引
```

### 修改时
```
修改文件 → 检测变更范围 → 重新分块（变更部分）→ 更新 Embedding → 更新 chunks.json → 标记相关文件 "needs_review"
```

### 删除时
```
删除文件 → 级联删除所有相关 chunks → 更新所有索引文件
```

## 实现优先级

| 优先级 | 功能 | 说明 |
|--------|------|------|
| P0 | 结构化索引（index.json, character_graph.json） | 最基础，必须实现 |
| P0 | 一致性检查引擎 | 保障数据质量 |
| P1 | 关键词倒排索引 | 轻量检索，快速实现 |
| P1 | 查询分类器 | 提升检索精准度 |
| P2 | 语义 Embedding | 需要模型支持 |
| P2 | 混合检索 | 结构化+语义结合 |
| P3 | 增量更新优化 | 大规模项目时的性能优化 |
