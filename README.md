# Storyline Skill — 教育项目剧情创作系统

> 为教育项目提供结构化的剧情故事创作支持，核心服务于**直播课教学场景**（剧情穿插在老师 PPT 课件中）。

[English README](./README_EN.md)（即将推出）

---

## 📖 项目介绍

Storyline Skill 是一套面向教育场景的剧情故事创作技能系统，帮助教师/内容创作者将**教学知识点**与**剧情故事**有机结合，生成可直接用于课堂教学的结构化素材。

### 核心场景

- **直播课教学**：老师通过 PPT 教学，剧情以**轻量节点**形式穿插在课件中
- **动画分镜输出**：开头和结尾的完整动画剧情，输出**分镜脚本**供动画制作
- **AI 互动课预留**：为后续录播 AI 互动课预留扩展接口

### 叙事结构

每课时采用**三幕式**结构，以"钩子"贯穿：

```
第一幕：开场动画（1-2 分钟）
  └── 角色登场 + 遭遇困境 → 抛出与知识点相关的悬念钩子

第二幕：中间教学（穿插式剧情节点）
  └── 学习知识点 → 完成练习 → 剧情逐步推进（回收钩子）

第三幕：结尾动画（1-2 分钟）
  └── 解决困境 → 本课收束 → 下集预告（如适用）
```

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **主技能 + 5 子技能** | 职责清晰，可独立迭代 |
| **三步确认机制** | 梗概确认 → 节点确认 → 分镜确认，不自动推进 |
| **角色跨学科一致性** | 同一角色跨学科性格一致，仅允许微小适配 |
| **认知水平自动适配** | 根据年级调整台词风格、情节复杂度 |
| **钩子贯穿设计** | 开场抛悬念 → 中间逐步回收 → 结尾解决 + 新悬念 |
| **知识管理（RAG）** | 自动索引维护，支持自然语言检索 |
| **一致性检查引擎** | 自动检测角色/世界观/剧情逻辑冲突 |
| **低年级 ↔ 高年级全覆盖** | 从三年级童话到初二悬疑，支持复杂叙事 |

---

## 🏗️ 系统架构

```
storyline-director（主技能 / 调度器）
│
├── character-manager（角色管理）
│   ├── 创建/读取角色档案
│   ├── 角色一致性检查
│   └── 跨学科适配
│
├── world-builder（世界观构建）
│   ├── 创建/读取世界观
│   └── 世界观一致性维护
│
├── story-outline（故事梗概生成）
│   ├── 知识点分析
│   ├── 角色匹配
│   ├── 钩子设计
│   └── 生成故事梗概（等待确认）
│
├── teaching-nodes（教学节点设计）
│   ├── 拆分教学进度
│   ├── 设计剧情节点与教学抓手
│   └── 生成节点清单（等待确认）
│
└── script-writer（脚本撰写 — 核心）
    ├── 开场分镜脚本
    ├── 结尾分镜脚本
    └── 节点对白脚本
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/hughtty/storyline-skill.git
cd storyline-skill
```

### 2. 项目结构

```
storyline-skill/
│
├── .claude/skills/              # Claude Code 技能定义
│   ├── storyline-director/      # 主技能
│   ├── character-manager/       # 角色管理
│   ├── world-builder/           # 世界观构建
│   ├── story-outline/           # 故事梗概
│   ├── teaching-nodes/          # 教学节点
│   └── script-writer/           # 脚本撰写
│
├── templates/                   # 模板文件
│   ├── character/               # 角色档案模板
│   ├── worldview/               # 世界观模板
│   ├── episode/                 # 课时文件模板
│   └── project/                 # 项目元信息模板
│
├── tools/                       # 工具脚本
│   ├── consistency_checker.py   # 一致性检查引擎
│   ├── cognitive_level_guide.md # 认知水平适配参考
│   ├── storytelling_patterns.md # 剧情设计模式库
│   └── advanced_narrative_guide.md # 高年级复杂叙事指南
│
├── docs/architecture/           # 架构设计文档
│   ├── data-model.md            # 数据模型
│   ├── rag-system.md            # RAG 检索系统
│   └── consistency-engine.md    # 一致性检查引擎
│
├── examples/                    # 示例项目
│   └── demo-project/            # "魔法英语学院"完整示例
│
└── test-run/                    # 测试输出
    ├── ep01/                    # 低年级测试（分数蛋糕）
    └── test-run-advanced/ep01/  # 高年级测试（证据谎言）
```

### 3. 使用流程

```
Step 1: 项目初始化（新建 / 延续）
Step 2: 需求采集（学科、知识点、年级、角色）
Step 3: 故事梗概 → 等待用户确认 ✓
Step 4: 教学节点 → 等待用户确认 ✓
Step 5: 结尾衔接确认（是否单元结束？下集知识点？）
Step 6: 脚本撰写 → 等待用户 review
Step 7: 交付
```

---

## 📋 技能说明

| 技能 | 职责 | 输出文件 |
|------|------|----------|
| **storyline-director** | 主调度器，管理项目生命周期和确认流程 | 项目结构 |
| **character-manager** | 角色档案、一致性、跨学科适配 | 角色 Markdown 档案 |
| **world-builder** | 世界观创建与维护 | worldview.md |
| **story-outline** | 知识点匹配、钩子设计、梗概生成 | story_outline.md |
| **teaching-nodes** | 教学进度拆分、节点设计 | teaching_nodes.md |
| **script-writer** | 分镜脚本 + 对白撰写 | *_storyboard.md + node_scripts.md |

---

## 🎨 示例项目

### 示例 1：低年级 — 圆圆的分身之谜（数学 / 四年级 / 分数）

- **故事**：小智和圆形精灵圆圆发现魔法蛋糕，通过学会分数来平均分配
- **抓手**：钥匙模式（每学完一个分数 = 解开一把锁）
- **特点**：轻松愉快、单线叙事、角色扁平标签

[查看完整示例 →](examples/demo-project/)

### 示例 2：高年级 — 证据的谎言（英语 / 初二 / 定语从句）

- **故事**："语言之心"碎片被盗，小智和小慧用定语从句的精确描述穿透完美证据的谎言
- **抓手**：侦探推理（精确描述 = 发现证据漏洞）
- **特点**：悬疑烧脑、双层钩子、角色弧光、道德灰度、红鲱鱼误导

[查看完整示例 →](test-run-advanced/ep01/)

---

## 🔍 知识管理

### 自动索引维护

每完成一个课时，自动更新：
- `index.json` — 项目级索引
- `character_graph.json` — 角色关系图谱
- `episode_graph.json` — 课时关联图谱
- `knowledge_map.json` — 知识点映射

### 智能检索

支持自然语言查询：

| 查询类型 | 示例 |
|----------|------|
| 角色检索 | "找一个勇敢的角色" |
| 剧情检索 | "找有分数知识点的课时" |
| 对白检索 | "小智说过'让我来'吗？" |
| 跨课时追踪 | "ep01 的钩子在哪儿回收了？" |

### 一致性检查

```bash
python3 tools/consistency_checker.py /path/to/project
```

检查维度：角色一致性、世界观一致性、剧情逻辑、跨课时连续性。

---

## 📁 输出文件说明

| 文件 | 说明 | 使用者 |
|------|------|--------|
| `story_outline.md` | 故事梗概（角色分配、三幕结构、教学抓手） | 编剧、老师 |
| `teaching_nodes.md` | 教学节点清单（触发时机、对白、可选性标注） | 老师 |
| `opening_storyboard.md` | 开场动画分镜脚本 | 动画老师 |
| `ending_storyboard.md` | 结尾动画分镜脚本 | 动画老师 |
| `node_scripts.md` | 节点对白脚本（含视觉素材建议） | 老师、PPT 制作 |

---

## 🛠️ 工具脚本

### consistency_checker.py — 一致性检查引擎

```bash
# 检查整个项目
python3 tools/consistency_checker.py ./examples/demo-project

# 只检查指定角色
python3 tools/consistency_checker.py ./examples/demo-project --character 小智

# 只检查指定课时
python3 tools/consistency_checker.py ./examples/demo-project --episode ep01
```

输出：控制台摘要 + `consistency_log/latest_report.md`

---

## 📝 认知水平适配参考

| 维度 | 低年级（1-3 年级） | 中年级（4-6 年级） | 初中 |
|------|-------------------|-------------------|------|
| 台词风格 | 短句、语气词多 | 适当复杂句式 | 隐喻、讽刺 |
| 情节复杂度 | 单线，无反转 | 单线 + 1 个障碍 | 多线 + 悬念 |
| 人物关系 | 2-3 人，关系简单 | 3-4 人，小互动 | 复杂社会关系 |
| 道德灰度 | 无 | 轻微 | 允许灰色地带 |

[查看完整参考 →](tools/cognitive_level_guide.md)

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/xxx`
3. 提交更改：`git commit -m "Add xxx"`
4. 推送分支：`git push origin feature/xxx`
5. 创建 Pull Request

---

## 📄 许可证

MIT License — 详见 [LICENSE](./LICENSE) 文件。

---

## 🙏 致谢

本项目基于 [Claude Code](https://claude.ai/code) 技能系统构建，感谢 Anthropic 提供的能力支持。

---

> **Storyline Skill** — 让知识点在故事中生长 🌱
