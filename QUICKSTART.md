# Storyline Skill — 快速启动指南

## 目录结构总览

```
storyline skill/
│
├── README.md                          # 系统说明
├── QUICKSTART.md                      # 本文件
│
├── .claude/skills/                    # 技能定义目录
│   ├── storyline-director/            # 主技能：剧情导演
│   │   ├── SKILL.md                   #   技能定义
│   │   └── PROMPT.md                  #   执行指令
│   ├── character-manager/             # 子技能：角色管理
│   │   ├── SKILL.md
│   │   └── PROMPT.md
│   ├── world-builder/                 # 子技能：世界观构建
│   │   ├── SKILL.md
│   │   └── PROMPT.md
│   ├── story-outline/                 # 子技能：故事梗概
│   │   ├── SKILL.md
│   │   └── PROMPT.md
│   ├── teaching-nodes/                # 子技能：教学节点
│   │   ├── SKILL.md
│   │   └── PROMPT.md
│   └── script-writer/                 # 子技能：脚本撰写（核心）
│       ├── SKILL.md
│       └── PROMPT.md
│
├── templates/                         # 模板文件
│   ├── character/
│   │   └── character_template.md      # 角色档案模板
│   ├── worldview/
│   │   └── worldview_template.md      # 世界观模板
│   ├── episode/
│   │   ├── story_outline_template.md      # 故事梗概模板
│   │   ├── teaching_nodes_template.md     # 教学节点模板
│   │   ├── opening_storyboard_template.md # 开场分镜模板
│   │   ├── ending_storyboard_template.md  # 结尾分镜模板
│   │   └── node_scripts_template.md       # 节点对白模板
│   └── project/
│       └── meta.json                  # 项目元信息模板
│
├── tools/                             # 工具/参考文件
│   ├── cognitive_level_guide.md       # 认知水平适配参考表
│   └── storytelling_patterns.md       # 剧情设计模式库
│
└── examples/                          # 示例项目
    └── demo-project/                  # "魔法英语学院"示例
        ├── worldview.md
        ├── shared_library/
        │   └── characters/
        │       └── ip/
        │           ├── 小智.md
        │           └── 小慧.md
        └── episodes/
            └── ep01/
                ├── story_outline.md
                ├── teaching_nodes.md
                ├── opening_storyboard.md
                ├── ending_storyboard.md
                └── node_scripts.md
```

## 使用流程

### 1. 启动创作

用户在 Claude Code 中输入项目信息，触发 `storyline-director`：

```
用户："我要做一个新项目的英语课，三年级，知识点是一般现在时"

系统：
1. 创建项目目录
2. 询问/创建世界观
3. 询问/选择角色
4. 采集完整需求
```

### 2. 分阶段确认（严格执行）

```
Stage 1: 故事梗概
  → 输出 story_outline.md
  → 等待用户确认 ✓

Stage 2: 教学节点
  → 输出 teaching_nodes.md
  → 等待用户确认 ✓

Stage 3: 结尾衔接
  → 确认是否单元结束
  → 确认下集知识点（如适用）

Stage 4: 脚本输出
  → 输出 opening_storyboard.md
  → 输出 node_scripts.md
  → 输出 ending_storyboard.md
  → 等待用户 review
```

### 3. 项目文件产出

最终交付物：
- `story_outline.md` — 故事梗概（含角色分配、三幕结构、教学抓手）
- `teaching_nodes.md` — 教学节点清单（含触发时机、对白、可选性标注）
- `opening_storyboard.md` — 开场动画分镜脚本
- `ending_storyboard.md` — 结尾动画分镜脚本
- `node_scripts.md` — 节点对白脚本（含视觉素材建议）

## 快速参考

### 认知水平速查

| 年级 | 台词风格 | 情节复杂度 | 人物关系 |
|------|----------|------------|----------|
| 1-2 年级 | 短句、语气词多 | 单线，无反转 | 2-3 人，关系简单 |
| 3-4 年级 | 适当复杂句式 | 单线+1个障碍 | 3-4 人，小互动 |
| 5-6 年级 | 复杂表达 | 多线+1-2反转 | 4-5 人，较复杂 |
| 初中 | 青少年口语 | 多线+悬念 | 复杂社会关系 |

### 钩子设计速查

| 模式 | 适用知识点 | 示例 |
|------|-----------|------|
| 困境型 | 逻辑性强的知识点 | 门锁密码=语法规则 |
| 寻找型 | 词汇、概念类 | 找关键词=核心概念 |
| 修复型 | 规则、流程类 | 机器故障=运算错误 |
| 竞争型 | 需练习熟练度 | 答题闯关=口算练习 |

### 教学抓手速查

| 模式 | 结构 |
|------|------|
| 钥匙模式 | 每个知识点=一把钥匙，集齐开门 |
| 拼图模式 | 每个知识点=一块拼图，拼完揭示答案 |
| 升级模式 | 每个知识点=一次升级，满级战胜困难 |
| 破译模式 | 每个知识点=一条线索，破译密码 |

## 示例项目说明

`examples/demo-project/` 包含一个完整的示例：

- **项目名称**：魔法英语学院
- **课时**：第1课 — 被封印的魔法书
- **学科**：英语
- **年级**：三年级
- **知识点**：一般现在时
- **角色**：小智（勇敢莽撞）、小慧（聪明谨慎）
- **故事**：在魔法图书馆发现被封印的书，通过学会一般现在时解开三把锁

可直接查看示例了解完整的输出格式和质量标准。
