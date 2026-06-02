#!/usr/bin/env python3
"""
Storyline Skill — 一致性检查引擎
自动检测项目中的角色、世界观、剧情逻辑、跨课时连续性问题

用法：
    python consistency_checker.py /path/to/project
    python consistency_checker.py /path/to/project --character 小智
    python consistency_checker.py /path/to/project --episode ep01

输出：
    控制台输出检查摘要
    写入 consistency_log/latest_report.md（完整报告）
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class Severity(Enum):
    CRITICAL = "🔴"   # 严重：必须修复
    WARNING = "🟡"    # 警告：建议修复
    INFO = "🟢"       # 提示：可选修复


@dataclass
class Violation:
    severity: Severity
    dimension: str       # 检查维度：角色/世界观/剧情逻辑/跨课时
    rule: str            # 具体规则
    file: str            # 相关文件
    description: str     # 问题描述
    suggestion: str      # 修复建议
    line_hint: Optional[str] = None  # 可能的问题位置


class ConsistencyChecker:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.violations: List[Violation] = []
        self.project_data = {}
        self.index = {}
        self.character_graph = {}
        self.episode_graph = {}
        self.worldview = ""
        self.characters = {}       # name -> parsed character data
        self.episodes = {}         # ep_id -> parsed episode data

    def load_project(self) -> bool:
        """加载项目索引文件"""
        index_file = self.project_path / "index.json"
        if not index_file.exists():
            self.violations.append(Violation(
                severity=Severity.CRITICAL,
                dimension="项目结构",
                rule="项目索引必须存在",
                file=str(index_file),
                description="未找到 index.json，项目索引不完整",
                suggestion="运行项目初始化，重新生成索引文件"
            ))
            return False

        with open(index_file, 'r', encoding='utf-8') as f:
            self.index = json.load(f)

        # 加载角色图谱
        char_graph_file = self.project_path / "character_graph.json"
        if char_graph_file.exists():
            with open(char_graph_file, 'r', encoding='utf-8') as f:
                self.character_graph = json.load(f)

        # 加载课时图谱
        ep_graph_file = self.project_path / "episode_graph.json"
        if ep_graph_file.exists():
            with open(ep_graph_file, 'r', encoding='utf-8') as f:
                self.episode_graph = json.load(f)

        # 加载世界观
        worldview_file = self.project_path / "worldview.md"
        if worldview_file.exists():
            with open(worldview_file, 'r', encoding='utf-8') as f:
                self.worldview = f.read()

        return True

    def load_characters(self):
        """加载所有角色档案"""
        char_dir = self.project_path / "shared_library" / "characters"
        if not char_dir.exists():
            return

        for char_type in ["ip", "npc"]:
            type_dir = char_dir / char_type
            if not type_dir.exists():
                continue
            for md_file in type_dir.glob("*.md"):
                name = md_file.stem
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.characters[name] = self._parse_character(content, str(md_file))

    def load_episodes(self):
        """加载所有课时文件"""
        ep_dir = self.project_path / "episodes"
        if not ep_dir.exists():
            return

        for ep_dir_path in ep_dir.iterdir():
            if not ep_dir_path.is_dir():
                continue
            ep_id = ep_dir_path.name
            self.episodes[ep_id] = {}

            # 加载各文件
            for file_name in ["story_outline.md", "teaching_nodes.md", "node_scripts.md"]:
                file_path = ep_dir_path / file_name
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.episodes[ep_id][file_name] = f.read()

    def _parse_character(self, content: str, file_path: str) -> Dict:
        """解析角色 Markdown 档案，提取关键字段"""
        data = {
            "file": file_path,
            "core_personality": "",
            "appearances": [],
            "subjects": [],
            "type": "",
        }

        # 从 frontmatter 提取
        frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            fm = frontmatter_match.group(1)
            # 解析 type
            type_match = re.search(r'type:\s*(\S+)', fm)
            if type_match:
                data["type"] = type_match.group(1)
            # 解析 subjects
            subjects_match = re.search(r'subjects:\s*\[(.*?)\]', fm)
            if subjects_match:
                subjects_str = subjects_match.group(1)
                data["subjects"] = [s.strip().strip('"').strip("'") for s in subjects_str.split(',')]

        # 从内容提取核心性格
        personality_match = re.search(r'### 性格.*?\n- 核心性格特征：(.+?)(?:\n|$)', content)
        if personality_match:
            data["core_personality"] = personality_match.group(1).strip()

        # 提取出场记录
        appearances = re.findall(
            r'\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(.*?)\s*\|',
            content
        )
        for row in appearances:
            if row[0] != '项目':  # 跳过表头
                data["appearances"].append({
                    "project": row[0],
                    "episode": row[1],
                    "subject": row[2],
                    "role": row[3],
                    "note": row[4]
                })

        return data

    # ============================================================
    # 检查维度 1：角色一致性
    # ============================================================

    def check_character_consistency(self, character_name: Optional[str] = None):
        """检查角色一致性"""
        targets = [character_name] if character_name else list(self.characters.keys())

        for name in targets:
            if name not in self.characters:
                continue
            char_data = self.characters[name]

            # 检查 1.1：角色档案中核心性格是否为空
            if not char_data["core_personality"]:
                self.violations.append(Violation(
                    severity=Severity.WARNING,
                    dimension="角色一致性",
                    rule="角色核心性格必须定义",
                    file=char_data["file"],
                    description=f"角色 '{name}' 未定义核心性格",
                    suggestion="在角色档案中补充核心性格特征"
                ))

            # 检查 1.2：课时中的性格描述与核心性格是否偏离
            self._check_character_in_episodes(name, char_data)

            # 检查 1.3：出场记录与 index.json 是否一致
            self._check_character_appearances_index(name, char_data)

    def _check_character_in_episodes(self, name: str, char_data: Dict):
        """检查角色在各课时中的性格描述是否与核心一致"""
        core_personality = char_data.get("core_personality", "")
        if not core_personality:
            return

        core_keywords = self._extract_personality_keywords(core_personality)

        for ep_id, ep_files in self.episodes.items():
            outline = ep_files.get("story_outline.md", "")
            nodes = ep_files.get("teaching_nodes.md", "")
            scripts = ep_files.get("node_scripts.md", "")

            # 检查 story_outline 中的性格适配说明
            if name in outline:
                # 查找性格适配描述
                adapt_match = re.search(
                    rf'\|?\s*{re.escape(name)}\s*\|.*?\|\s*(.*?)\s*\|',
                    outline
                )
                if adapt_match:
                    adapt_desc = adapt_match.group(1)
                    # 检查是否有巨大偏离
                    if self._is_major_deviation(core_keywords, adapt_desc):
                        self.violations.append(Violation(
                            severity=Severity.WARNING,
                            dimension="角色一致性",
                            rule="跨课时核心性格不可擅自修改",
                            file=f"episodes/{ep_id}/story_outline.md",
                            description=f"角色 '{name}' 在 {ep_id} 中的性格描述 '{adapt_desc}' 可能与核心性格 '{core_personality}' 有偏离",
                            suggestion="确认是否为角色成长弧光，如不是请修正"
                        ))

            # 检查 node_scripts 中对白是否符合性格
            if scripts and name in scripts:
                self._check_dialogue_personality(name, core_personality, scripts, ep_id)

    def _extract_personality_keywords(self, personality: str) -> List[str]:
        """从性格描述中提取关键词"""
        # 常见性格关键词映射
        keyword_map = {
            "勇敢": ["勇敢", "大胆", "无畏", "敢"],
            "莽撞": ["莽撞", "冲动", "急躁", "不经思考"],
            "聪明": ["聪明", "智慧", "机智", "分析"],
            "谨慎": ["谨慎", "小心", "冷静", "稳重"],
            "活泼": ["活泼", "开朗", "热情"],
            "内向": ["内向", "安静", "沉默"],
        }
        found = []
        for trait, keywords in keyword_map.items():
            for kw in keywords:
                if kw in personality:
                    found.append(trait)
                    break
        return found

    def _is_major_deviation(self, core_keywords: List[str], adapt_desc: str) -> bool:
        """判断是否为主要偏离"""
        # 简单规则：如果核心关键词在适配描述中完全找不到，视为偏离
        if not core_keywords:
            return False

        # 反义词检测
        antonym_map = {
            "勇敢": ["胆小", "害怕", "懦弱"],
            "莽撞": ["冷静", "谨慎", "稳重", "深思熟虑"],
            "聪明": ["愚笨", "迟钝", "傻"],
            "谨慎": ["冲动", "莽撞", "大胆"],
        }

        for trait in core_keywords:
            if trait in antonym_map:
                for antonym in antonym_map[trait]:
                    if antonym in adapt_desc:
                        return True
        return False

    def _check_dialogue_personality(self, name: str, core_personality: str, scripts: str, ep_id: str):
        """检查对白是否符合角色性格"""
        # 提取该角色的所有对白
        dialogue_pattern = rf'\*\*{re.escape(name)}\*\*.*?\n>\s*(.+)'
        dialogues = re.findall(dialogue_pattern, scripts)

        if not dialogues:
            return

        # 简单启发式：检查对白长度和复杂度是否匹配角色年级
        # 低年级角色不应有过长/过复杂的对白
        for line in dialogues:
            if len(line) > 100:  # 超过100字的对白
                # 检查是否为高年级项目
                grade = self.index.get("settings", {}).get("default_grade", "")
                if "低" in grade or "1" in grade or "2" in grade or "3" in grade:
                    self.violations.append(Violation(
                        severity=Severity.INFO,
                        dimension="角色一致性",
                        rule="对白应符合认知水平",
                        file=f"episodes/{ep_id}/node_scripts.md",
                        description=f"角色 '{name}' 的对白过长（{len(line)}字），可能不符合低年级认知水平",
                        suggestion="检查是否需要简化台词",
                        line_hint=line[:50] + "..."
                    ))

    def _check_character_appearances_index(self, name: str, char_data: Dict):
        """检查角色出场记录与 index.json 是否一致"""
        index_chars = self.index.get("characters_index", {})
        if name not in index_chars:
            return

        index_count = index_chars[name].get("appearances_count", 0)
        actual_count = len(char_data.get("appearances", []))

        if index_count != actual_count:
            self.violations.append(Violation(
                severity=Severity.WARNING,
                dimension="角色一致性",
                rule="出场记录应与索引一致",
                file=f"shared_library/characters/{char_data['type']}/{name}.md",
                description=f"角色 '{name}' 索引显示出场 {index_count} 次，实际档案记录 {actual_count} 次",
                suggestion="更新 index.json 或角色档案中的出场记录"
            ))

    # ============================================================
    # 检查维度 2：世界观一致性
    # ============================================================

    def check_worldview_consistency(self):
        """检查世界观一致性"""
        if not self.worldview:
            self.violations.append(Violation(
                severity=Severity.CRITICAL,
                dimension="世界观一致性",
                rule="世界观文档必须存在",
                file="worldview.md",
                description="未找到世界观文档",
                suggestion="创建 worldview.md"
            ))
            return

        # 检查 2.1：提取世界观中的核心场景，与课时场景对比
        scenes = self._extract_worldview_scenes()

        for ep_id, ep_files in self.episodes.items():
            outline = ep_files.get("story_outline.md", "")
            opening = ep_files.get("opening_storyboard.md", "")
            ending = ep_files.get("ending_storyboard.md", "")

            combined = outline + opening + ending

            # 检查课时中提到的场景是否在世界观中有定义
            for scene_name, scene_desc in scenes.items():
                if scene_name in combined:
                    # 场景被使用了，检查课时描述是否与世界观一致
                    pass  # 更复杂的语义对比需要 LLM，此处简化

        # 检查 2.2：世界观摘要与文档内容是否匹配
        summary = self.index.get("worldview_summary", "")
        if not summary:
            self.violations.append(Violation(
                severity=Severity.INFO,
                dimension="世界观一致性",
                rule="项目索引应包含世界观摘要",
                file="index.json",
                description="index.json 中 worldview_summary 为空",
                suggestion="添加世界观摘要，便于快速检索"
            ))

    def _extract_worldview_scenes(self) -> Dict[str, str]:
        """从世界观文档中提取场景定义"""
        scenes = {}
        # 匹配 ### 重要地点 表格
        table_match = re.search(r'### 重要地点\n(.*?)(?=##|\Z)', self.worldview, re.DOTALL)
        if table_match:
            table_content = table_match.group(1)
            rows = re.findall(r'\|\s*(\S+)\s*\|\s*(.*?)\s*\|', table_content)
            for row in rows:
                if row[0] != '名称':
                    scenes[row[0]] = row[1]
        return scenes

    # ============================================================
    # 检查维度 3：剧情逻辑一致性
    # ============================================================

    def check_story_logic(self, episode_filter: Optional[str] = None):
        """检查剧情逻辑一致性"""
        targets = [episode_filter] if episode_filter else list(self.episodes.keys())

        for ep_id in targets:
            if ep_id not in self.episodes:
                continue
            ep_data = self.episodes[ep_id]

            outline = ep_data.get("story_outline.md", "")
            nodes = ep_data.get("teaching_nodes.md", "")

            # 检查 3.1：钩子是否有回收
            self._check_hook_recovery(ep_id, outline, nodes)

            # 检查 3.2：教学抓手是否有对应节点
            self._check_teaching_nodes_mapping(ep_id, outline, nodes)

            # 检查 3.3：故事梗概中的角色是否在节点中出现
            self._check_character_presence(ep_id, outline, nodes)

    def _check_hook_recovery(self, ep_id: str, outline: str, nodes: str):
        """检查开场钩子是否有回收"""
        # 从梗概中提取钩子
        hook_match = re.search(r'【钩子】：(.+?)(?:\n|$)', outline)
        if not hook_match:
            self.violations.append(Violation(
                severity=Severity.WARNING,
                dimension="剧情逻辑",
                rule="故事梗概应包含钩子设计",
                file=f"episodes/{ep_id}/story_outline.md",
                description=f"{ep_id} 未找到明确的钩子设计",
                suggestion="在故事梗概中补充钩子设计"
            ))
            return

        hook = hook_match.group(1).strip()

        # 检查教学节点中是否有钩子回收
        if "钩子回收" not in nodes and "钩子" not in nodes:
            self.violations.append(Violation(
                severity=Severity.CRITICAL,
                dimension="剧情逻辑",
                rule="开场钩子必须在教学节点中有回收",
                file=f"episodes/{ep_id}/teaching_nodes.md",
                description=f"{ep_id} 的教学节点未提及钩子回收进度",
                suggestion="在节点详情中添加钩子回收进度表"
            ))

        # 检查结尾是否有钩子回收
        if "钩子回收" not in outline:
            ending_section = re.search(r'### 第三幕.*?(?=##|\Z)', outline, re.DOTALL)
            if ending_section and "钩子回收" not in ending_section.group(0):
                self.violations.append(Violation(
                    severity=Severity.WARNING,
                    dimension="剧情逻辑",
                    rule="结尾应有钩子回收说明",
                    file=f"episodes/{ep_id}/story_outline.md",
                    description=f"{ep_id} 的第三幕未明确说明钩子回收方式",
                    suggestion="补充钩子回收的具体情节"
                ))

    def _check_teaching_nodes_mapping(self, ep_id: str, outline: str, nodes: str):
        """检查教学抓手与节点是否对应"""
        # 从梗概中提取抓手数量
        grip_count = len(re.findall(r'\|[^\n]*\|[^\n]*\|[^\n]*\|[^\n]*\|', outline))
        # 简化的计数方式，实际应更精确

        # 从节点清单中提取节点数量
        node_count = len(re.findall(r'### 节点 \d+', nodes))

        if grip_count > 0 and node_count == 0:
            self.violations.append(Violation(
                severity=Severity.CRITICAL,
                dimension="剧情逻辑",
                rule="教学抓手必须有对应的教学节点",
                file=f"episodes/{ep_id}/teaching_nodes.md",
                description=f"{ep_id} 有教学抓手但无教学节点",
                suggestion="根据抓手设计拆分教学节点"
            ))

    def _check_character_presence(self, ep_id: str, outline: str, nodes: str):
        """检查梗概中的角色是否在节点对白中出现"""
        # 从角色分配表中提取角色名
        char_section = re.search(r'## 角色任务分配\n(.*?)(?=##|\Z)', outline, re.DOTALL)
        if not char_section:
            return

        char_table = char_section.group(1)
        # 解析表格：按行分割，取第一列（角色名）
        char_names = []
        for line in char_table.strip().split('\n'):
            line = line.strip()
            if not line or '---' in line:
                continue
            if line.startswith('|'):
                cols = [c.strip() for c in line.split('|')]
                cols = [c for c in cols if c]
                if cols and cols[0] != '角色':
                    char_names.append(cols[0])

        scripts = self.episodes[ep_id].get("node_scripts.md", "")

        for name in char_names:
            if name in outline and name not in scripts and scripts:
                self.violations.append(Violation(
                    severity=Severity.INFO,
                    dimension="剧情逻辑",
                    rule="梗概中的角色应在节点对白中出现",
                    file=f"episodes/{ep_id}/node_scripts.md",
                    description=f"角色 '{name}' 在梗概中出现，但在节点对白中未找到",
                    suggestion="检查是否需要为该角色补充对白"
                ))

    # ============================================================
    # 检查维度 4：跨课时连续性
    # ============================================================

    def check_cross_episode_continuity(self):
        """检查跨课时连续性"""
        edges = self.episode_graph.get("edges", [])
        nodes = self.episode_graph.get("nodes", {})

        # 检查 4.1：主线课时的结尾预告与下一集开头是否衔接
        main_line = self.index.get("storylines", {}).get("main", [])

        for i in range(len(main_line) - 1):
            current_ep = main_line[i]
            next_ep = main_line[i + 1]

            current_data = nodes.get(current_ep, {})
            next_data = nodes.get(next_ep, {})

            # 检查当前课时是否有下集预告
            if not current_data.get("next_episode_hint"):
                self.violations.append(Violation(
                    severity=Severity.INFO,
                    dimension="跨课时连续",
                    rule="主线课时应有下集预告",
                    file=f"episodes/{current_ep}/story_outline.md",
                    description=f"主线课时 {current_ep} 未设置下集预告，与 {next_ep} 的衔接可能不自然",
                    suggestion="在故事梗概中补充下集预告"
                ))

        # 检查 4.2：活跃钩子是否有过期未回收的
        hooks = self.episode_graph.get("hooks_registry", {}).get("active_hooks", [])
        for hook in hooks:
            projected = hook.get("projected_recovery_episode")
            if projected:
                # 检查 projected 课时是否已存在
                if projected not in nodes:
                    self.violations.append(Violation(
                        severity=Severity.WARNING,
                        dimension="跨课时连续",
                        rule="预告的钩子应有回收课时",
                        file="episode_graph.json",
                        description=f"钩子 '{hook['description']}' 预计在 {projected} 回收，但该课时尚未创建",
                        suggestion=f"创建 {projected} 并在其中回收该钩子"
                    ))

    # ============================================================
    # 报告生成
    # ============================================================

    def run_all_checks(self, character: Optional[str] = None, episode: Optional[str] = None):
        """运行全部检查"""
        print("=" * 60)
        print("Storyline Skill — 一致性检查引擎")
        print(f"项目：{self.project_path.name}")
        print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        if not self.load_project():
            return

        self.load_characters()
        self.load_episodes()

        print("\n📋 加载状态")
        print(f"  角色数：{len(self.characters)}")
        print(f"  课时数：{len(self.episodes)}")
        print(f"  世界观：{'✅' if self.worldview else '❌'}")

        print("\n🔍 开始检查...\n")

        # 维度 1
        print("[1/4] 检查角色一致性...")
        self.check_character_consistency(character)

        # 维度 2
        print("[2/4] 检查世界观一致性...")
        self.check_worldview_consistency()

        # 维度 3
        print("[3/4] 检查剧情逻辑...")
        self.check_story_logic(episode)

        # 维度 4
        print("[4/4] 检查跨课时连续性...")
        self.check_cross_episode_continuity()

        self._print_summary()
        self._write_report()

    def _print_summary(self):
        """打印检查摘要"""
        critical = sum(1 for v in self.violations if v.severity == Severity.CRITICAL)
        warning = sum(1 for v in self.violations if v.severity == Severity.WARNING)
        info = sum(1 for v in self.violations if v.severity == Severity.INFO)

        print("\n" + "=" * 60)
        print("📊 检查结果摘要")
        print("=" * 60)
        print(f"  🔴 严重冲突：{critical}")
        print(f"  🟡 警告冲突：{warning}")
        print(f"  🟢 提示信息：{info}")
        print(f"  📋 总计：{len(self.violations)}")

        if critical > 0:
            print("\n🔴 严重冲突（必须修复）：")
            for v in self.violations:
                if v.severity == Severity.CRITICAL:
                    print(f"  [{v.dimension}] {v.rule}")
                    print(f"    📄 {v.file}")
                    print(f"    💡 {v.suggestion}")

        if warning > 0:
            print("\n🟡 警告冲突（建议修复）：")
            for v in self.violations:
                if v.severity == Severity.WARNING:
                    print(f"  [{v.dimension}] {v.rule}")
                    print(f"    📄 {v.file}")
                    print(f"    💡 {v.suggestion}")

        print(f"\n📝 完整报告已写入：consistency_log/latest_report.md")

    def _write_report(self):
        """写入完整报告到文件"""
        log_dir = self.project_path / "consistency_log"
        log_dir.mkdir(exist_ok=True)

        report_path = log_dir / "latest_report.md"

        critical = [v for v in self.violations if v.severity == Severity.CRITICAL]
        warning = [v for v in self.violations if v.severity == Severity.WARNING]
        info = [v for v in self.violations if v.severity == Severity.INFO]

        lines = [
            "# 一致性检查报告",
            "",
            f"**项目**：{self.project_path.name}",
            f"**检查时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**检查范围**：{'指定角色/课时' if self.episodes and (self.project_path / 'episodes').exists() and len(self.episodes) < len(list((self.project_path / 'episodes').iterdir())) else '全项目'}",
            "",
            "## 统计",
            "",
            f"| 级别 | 数量 |",
            f"|------|------|",
            f"| 🔴 严重 | {len(critical)} |",
            f"| 🟡 警告 | {len(warning)} |",
            f"| 🟢 提示 | {len(info)} |",
            f"| **总计** | **{len(self.violations)}** |",
            "",
        ]

        if critical:
            lines.extend([
                "## 🔴 严重冲突（必须修复）",
                "",
            ])
            for i, v in enumerate(critical, 1):
                lines.extend([
                    f"### 冲突 #{i}",
                    f"- **维度**：{v.dimension}",
                    f"- **规则**：{v.rule}",
                    f"- **文件**：`{v.file}`",
                    f"- **描述**：{v.description}",
                    f"- **建议**：{v.suggestion}",
                    "",
                ])

        if warning:
            lines.extend([
                "## 🟡 警告冲突（建议修复）",
                "",
            ])
            for i, v in enumerate(warning, 1):
                lines.extend([
                    f"### 冲突 #{i}",
                    f"- **维度**：{v.dimension}",
                    f"- **规则**：{v.rule}",
                    f"- **文件**：`{v.file}`",
                    f"- **描述**：{v.description}",
                    f"- **建议**：{v.suggestion}",
                    "",
                ])

        if info:
            lines.extend([
                "## 🟢 提示信息（可选修复）",
                "",
            ])
            for i, v in enumerate(info, 1):
                lines.extend([
                    f"### 提示 #{i}",
                    f"- **维度**：{v.dimension}",
                    f"- **规则**：{v.rule}",
                    f"- **文件**：`{v.file}`",
                    f"- **描述**：{v.description}",
                    f"- **建议**：{v.suggestion}",
                    "",
                ])

        lines.extend([
            "---",
            "",
            "*报告由 Storyline Skill 一致性检查引擎自动生成*",
        ])

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description="Storyline Skill 一致性检查引擎")
    parser.add_argument("project", help="项目路径")
    parser.add_argument("--character", help="只检查指定角色", default=None)
    parser.add_argument("--episode", help="只检查指定课时", default=None)

    args = parser.parse_args()

    checker = ConsistencyChecker(args.project)
    checker.run_all_checks(character=args.character, episode=args.episode)


if __name__ == "__main__":
    main()
