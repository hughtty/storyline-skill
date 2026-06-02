# Storyline Skill — 数据模型与存储架构

## 设计目标

1. **快速检索**：用户能秒级找到任何角色、世界观、课时剧情
2. **关系追踪**：角色出场历史、课时关联、知识点映射一目了然
3. **一致性保障**：自动检测角色性格冲突、世界观矛盾、剧情漏洞
4. **RAG 友好**：支持语义检索，能用自然语言查询剧情内容
5. **增量扩展**：新增课时/角色时，索引自动更新，不影响已有数据

---

## 核心数据模型

### 1. 全局索引（Global Index）

文件：`~/.storyline-registry/projects.json`

```json
{
  "version": "1.0",
  "last_updated": "2024-06-02T12:00:00Z",
  "projects": [
    {
      "project_id": "magic-english-academy",
      "name": "魔法英语学院",
      "subject": "英语",
      "created_at": "2024-06-01",
      "updated_at": "2024-06-02",
      "path": "/Users/misssu/Documents/storyline skill/projects/magic-english-academy",
      "episode_count": 5,
      "character_count": 8,
      "status": "active"
    }
  ]
}
```

### 2. 项目级索引（Project Index）

文件：`{project}/index.json`

```json
{
  "project_id": "magic-english-academy",
  "name": "魔法英语学院",
  "subject": "英语",
  "worldview_summary": "魔法世界，语言能力=魔法能量",
  "characters": {
    "ip": ["小智", "小慧"],
    "npc": ["老猫头鹰教授", "小黑猫", "圆圆"]
  },
  "episodes": [
    {
      "episode_id": "ep01",
      "title": "被封印的魔法书",
      "knowledge_point": "一般现在时",
      "grade": "三年级",
      "episode_type": "主线",
      "status": "completed",
      "created_at": "2024-06-01",
      "files": {
        "story_outline": "episodes/ep01/story_outline.md",
        "teaching_nodes": "episodes/ep01/teaching_nodes.md",
        "opening_storyboard": "episodes/ep01/opening_storyboard.md",
        "ending_storyboard": "episodes/ep01/ending_storyboard.md",
        "node_scripts": "episodes/ep01/node_scripts.md"
      }
    }
  ],
  "storylines": {
    "main": ["ep01", "ep02", "ep03"],
    "side": ["ep04"],
    "cross": {
      "arc-a": ["ep05", "ep06", "ep07"]
    }
  }
}
```

### 3. 角色图谱（Character Graph）

文件：`{project}/shared_library/character_graph.json`

```json
{
  "characters": {
    "小智": {
      "type": "ip",
      "core_personality": "勇敢但莽撞",
      "file": "characters/ip/小智.md",
      "subjects": ["英语", "语文"],
      "appearances": [
        {
          "episode_id": "ep01",
          "title": "被封印的魔法书",
          "subject": "英语",
          "role": "主角",
          "arc": "从莽撞到学会思考"
        },
        {
          "episode_id": "ep02",
          "title": "时间密室",
          "subject": "英语",
          "role": "主角",
          "arc": "理解过去与现在的关系"
        }
      ],
      "relationships": {
        "小慧": {
          "type": "搭档",
          "dynamic": "互补（冲动 vs 谨慎）",
          "evolution": "信任加深"
        },
        "老猫头鹰教授": {
          "type": "师徒",
          "dynamic": "尊敬但有质疑",
          "evolution": "发现教授的秘密"
        }
      },
      "consistency_hash": "sha256:abc123..."
    }
  }
}
```

### 4. 课时关联图（Episode Graph）

文件：`{project}/episode_graph.json`

```json
{
  "nodes": {
    "ep01": {
      "title": "被封印的魔法书",
      "type": "主线",
      "knowledge_point": "一般现在时",
      "grade": "三年级",
      "status": "completed",
      "files": {
        "story_outline": "episodes/ep01/story_outline.md",
        "teaching_nodes": "episodes/ep01/teaching_nodes.md",
        "opening_storyboard": "episodes/ep01/opening_storyboard.md",
        "ending_storyboard": "episodes/ep01/ending_storyboard.md",
        "node_scripts": "episodes/ep01/node_scripts.md"
      }
    }
  },
  "edges": [
    {
      "from": "ep01",
      "to": "ep02",
      "type": "主线延续",
      "relation": "ep01 结尾引出 ep02 的时间密室",
      "hook": "1/5 vs 1/8 分数比较"
    },
    {
      "from": "ep01",
      "to": "ep05",
      "type": "伏笔回收",
      "relation": "ep01 中预言的碎片在 ep05 出现",
      "hook": "语言之心的碎片"
    }
  ]
}
```

### 5. 知识点映射（Knowledge Map）

文件：`{project}/knowledge_map.json`

```json
{
  "subjects": {
    "英语": {
      "三年级": {
        "一般现在时": {
          "episodes": ["ep01"],
          "prerequisites": [],
          "next": ["一般过去时"],
          "characters_used": ["小智", "小慧"],
          "storyline_pattern": "钥匙模式",
          "cognitive_level": "低年级"
        }
      }
    }
  }
}
```

---

## 文件存储结构（最终版）

```
{project_name}/
│
├── README.md                          # 项目说明
├── meta.json                          # 项目元信息
├── index.json                         # 项目级索引（快速入口）
├── worldview.md                       # 世界观文档
├── worldview_chunks.json              # 世界观语义分块索引
│
├── character_graph.json               # 角色关系图谱
├── episode_graph.json                 # 课时关联图谱
├── knowledge_map.json                 # 知识点映射
│
├── shared_library/
│   ├── characters/
│   │   ├── ip/
│   │   │   ├── 小智.md
│   │   │   └── 小智.chunks.json       # 角色档案语义分块
│   │   └── npc/
│   │       └── 圆圆.md
│   └── characters_index.json          # 角色快速索引
│
├── episodes/
│   └── {episode_id}/
│       ├── story_outline.md
│       ├── story_outline.chunks.json
│       ├── teaching_nodes.md
│       ├── teaching_nodes.chunks.json
│       ├── opening_storyboard.md
│       ├── ending_storyboard.md
│       ├── node_scripts.md
│       └── episode_meta.json          # 课时元信息
│
└── consistency_log/                   # 一致性检查日志
    ├── checks.json
    └── violations/
        └── {timestamp}_violation.md
```

---

## 索引更新机制

### 创建新课时时的自动更新

```
1. 生成课时文件
2. 更新 index.json → episodes 列表
3. 更新 episode_graph.json → 添加 node + edges
4. 更新 character_graph.json → 更新角色出场记录
5. 更新 knowledge_map.json → 添加知识点映射
6. 生成语义分块（chunks）
7. 运行一致性检查
8. 如有冲突，写入 consistency_log
```

### 修改角色时的级联更新

```
1. 更新角色档案
2. 更新 character_graph.json
3. 检查所有涉及该角色的课时 → 标记为 "needs_review"
4. 运行一致性检查（跨课时）
5. 如有性格冲突，提醒用户
```

---

## RAG 检索接口设计

### 检索类型

| 查询类型 | 示例 | 检索范围 |
|----------|------|----------|
| **角色检索** | "找一个勇敢的角色" | character_graph + 角色档案 chunks |
| **剧情检索** | "找有分数知识点的课时" | knowledge_map + episode chunks |
| **对白检索** | "找小智说'让我来'的地方" | node_scripts chunks |
| **世界观检索** | "魔法学院有什么场景？" | worldview chunks |
| **关系检索** | "小智和小慧是什么关系？" | character_graph relationships |
| **跨课时检索** | "上节课的钩子是什么？" | episode_graph edges |

### 分块策略（Chunking Strategy）

每个 Markdown 文件按语义分块：

```json
{
  "file": "episodes/ep01/story_outline.md",
  "chunks": [
    {
      "id": "ep01-story-outline-01",
      "type": "基本信息",
      "content": "学科：英语，年级：三年级，知识点：一般现在时",
      "embedding": "vector: [...]"
    },
    {
      "id": "ep01-story-outline-02",
      "type": "角色任务",
      "content": "小智：遭遇困境型，在魔法图书馆发现被封印的书...",
      "embedding": "vector: [...]"
    },
    {
      "id": "ep01-story-outline-03",
      "type": "钩子设计",
      "content": "三把锁需要说出太阳升起、月亮落下、星星闪烁的规律...",
      "embedding": "vector: [...]"
    }
  ]
}
```

分块粒度：
- 角色档案：按字段分块（性格/外貌/背景/出场记录）
- 故事梗概：按段落分块（基本信息/角色分配/三幕结构/教学抓手）
- 教学节点：按节点分块（每个节点独立）
- 分镜脚本：按镜头分块（每个镜头独立）
- 节点对白：按场景分块（每个节点独立）
