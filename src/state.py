from typing import TypedDict, List, Dict, Any, Optional

class NovelState(TypedDict):
    """
    Represents the state of the novel generation process.

    === 原有字段 ===
    """
    synopsis: str                  # Full synopsis of the novel
    config: Optional[Dict[str, Any]]  # Configuration from user input

    # === 三层结构字段 ===
    novel_outline: Optional[Dict[str, Any]]        # 总纲（整个小说的大纲）
    volume_frameworks: Optional[List[Dict]]        # 所有卷的框架
    current_volume_index: int                      # 当前卷索引 (1-based)
    current_volume_outline: Optional[str]          # 当前卷的详细大纲

    # === 分层记忆字段 ===
    hot_memory: Optional[Dict[str, Any]]           # 热记忆（当前卷的详细记忆）
    cold_memory: Optional[Dict[str, Any]]          # 冷记忆（历史卷的压缩摘要）

    # === RAG 相关 ===
    rag_enabled: bool                               # 是否启用 RAG
    rag_storage_path: Optional[str]                 # RAG 存储路径

    # === 章节生成字段（保持兼容） ===
    world_bible: Dict[str, Any]    # Global world settings (Characters, Worldbuilding, Plot Tracks)
    chapters: List[Dict[str, Any]] # List of chapter summaries
    current_beats: str             # Current chapter beats/outline
    draft: str                     # Current chapter draft text
    iteration: int                 # Iteration count for current chapter refinement
    current_chapter_index: int     # Index of the chapter currently being written
    feedback: Optional[str]        # Feedback from the critic

    # === 质量检查报告 ===
    volume_review_reports: Optional[List[Dict]]    # 卷级审查报告
    milestone_reports: Optional[List[Dict]]        # 里程碑审查报告

