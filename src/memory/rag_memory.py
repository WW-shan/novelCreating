"""
RAG 记忆系统 - 基于 ChromaDB 的语义检索

轻量级 RAG：只存储摘要和伏笔，用于语义检索相似内容
"""

import os

# ChromaDB 是可选依赖
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB 未安装，RAG 功能将被禁用")
    print("   安装方法: pip install chromadb")


class NovelRAGMemory:
    """
    轻量 RAG 记忆系统

    只存储：
    - 章节摘要
    - 伏笔
    - 卷摘要

    用于语义检索相似情节、相关伏笔等
    """

    def __init__(self, novel_title, storage_path="./rag_storage"):
        """
        初始化 RAG 系统

        Args:
            novel_title: 小说标题（用作collection名）
            storage_path: 存储路径
        """
        if not CHROMADB_AVAILABLE:
            self.enabled = False
            return

        self.enabled = True
        self.novel_title = novel_title

        # 创建存储目录
        full_path = os.path.join(storage_path, novel_title)
        os.makedirs(full_path, exist_ok=True)

        try:
            # 使用本地持久化存储
            self.client = chromadb.PersistentClient(path=full_path)

            # 创建三个集合
            self.chapters_collection = self.client.get_or_create_collection(
                name="chapter_summaries",
                metadata={"description": "章节摘要向量库"}
            )

            self.threads_collection = self.client.get_or_create_collection(
                name="plot_threads",
                metadata={"description": "伏笔向量库"}
            )

            self.volumes_collection = self.client.get_or_create_collection(
                name="volume_summaries",
                metadata={"description": "卷摘要向量库"}
            )

            print(f"  ✅ RAG 系统已初始化: {full_path}")

        except Exception as e:
            print(f"  ⚠️  RAG 初始化失败: {str(e)[:50]}")
            self.enabled = False

    def add_chapter(self, chapter_index, summary, volume_index):
        """
        添加章节摘要到向量库

        Args:
            chapter_index: 章节索引
            summary: 章节摘要
            volume_index: 所属卷索引
        """
        if not self.enabled or not summary:
            return

        try:
            self.chapters_collection.add(
                documents=[summary],
                ids=[f"chapter_{chapter_index}"],
                metadatas=[{
                    "chapter": chapter_index,
                    "volume": volume_index,
                    "type": "chapter_summary"
                }]
            )
        except Exception as e:
            print(f"  ⚠️  RAG 添加章节失败: {str(e)[:50]}")

    def add_plot_thread(self, thread_text, created_at, importance=5):
        """
        添加伏笔到向量库

        Args:
            thread_text: 伏笔内容
            created_at: 创建章节
            importance: 重要性 (1-10)
        """
        if not self.enabled or not thread_text:
            return

        try:
            thread_id = f"thread_{created_at}_{hash(thread_text) % 10000}"

            self.threads_collection.add(
                documents=[thread_text],
                ids=[thread_id],
                metadatas=[{
                    "created_at": created_at,
                    "importance": importance,
                    "resolved": False
                }]
            )
        except Exception as e:
            print(f"  ⚠️  RAG 添加伏笔失败: {str(e)[:50]}")

    def add_volume_summary(self, volume_index, summary):
        """
        添加卷摘要到向量库

        Args:
            volume_index: 卷索引
            summary: 卷摘要
        """
        if not self.enabled or not summary:
            return

        try:
            self.volumes_collection.add(
                documents=[summary],
                ids=[f"volume_{volume_index}"],
                metadatas=[{
                    "volume": volume_index,
                    "type": "volume_summary"
                }]
            )
        except Exception as e:
            print(f"  ⚠️  RAG 添加卷摘要失败: {str(e)[:50]}")

    def mark_thread_resolved(self, thread_id):
        """标记伏笔已解决"""
        if not self.enabled:
            return

        try:
            self.threads_collection.update(
                ids=[thread_id],
                metadatas=[{"resolved": True}]
            )
        except Exception as e:
            print(f"  ⚠️  RAG 更新伏笔状态失败: {str(e)[:50]}")

    def retrieve_similar_chapters(self, query, current_chapter, top_k=5):
        """
        检索相似的历史章节

        Args:
            query: 查询文本（场景描述、情节）
            current_chapter: 当前章节（只检索历史）
            top_k: 返回数量

        Returns:
            list: 相似章节的摘要
        """
        if not self.enabled:
            return []

        try:
            results = self.chapters_collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"chapter": {"$lt": current_chapter}}
            )

            if results and results.get("documents"):
                return results["documents"][0]
            return []

        except Exception as e:
            print(f"  ⚠️  RAG 检索章节失败: {str(e)[:50]}")
            return []

    def retrieve_relevant_threads(self, query, top_k=3):
        """
        检索相关的未解决伏笔

        Args:
            query: 查询文本
            top_k: 返回数量

        Returns:
            list: 相关伏笔
        """
        if not self.enabled:
            return []

        try:
            results = self.threads_collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"resolved": False}
            )

            if results and results.get("documents"):
                return results["documents"][0]
            return []

        except Exception as e:
            print(f"  ⚠️  RAG 检索伏笔失败: {str(e)[:50]}")
            return []

    def retrieve_relevant_volumes(self, query, top_k=2):
        """
        检索相关的历史卷

        Args:
            query: 查询文本
            top_k: 返回数量

        Returns:
            list: 相关卷摘要
        """
        if not self.enabled:
            return []

        try:
            results = self.volumes_collection.query(
                query_texts=[query],
                n_results=top_k
            )

            if results and results.get("documents"):
                return results["documents"][0]
            return []

        except Exception as e:
            print(f"  ⚠️  RAG 检索卷摘要失败: {str(e)[:50]}")
            return []

    def retrieve_all_context(self, query, current_chapter):
        """
        一次性检索所有相关上下文

        Args:
            query: 查询文本（当前场景描述）
            current_chapter: 当前章节

        Returns:
            dict: {
                'similar_chapters': 相似章节,
                'relevant_threads': 相关伏笔,
                'relevant_volumes': 相关卷
            }
        """
        return {
            "similar_chapters": self.retrieve_similar_chapters(
                query, current_chapter, top_k=3
            ),
            "relevant_threads": self.retrieve_relevant_threads(
                query, top_k=3
            ),
            "relevant_volumes": self.retrieve_relevant_volumes(
                query, top_k=2
            )
        }


def create_rag_memory(novel_title, storage_path="./rag_storage", enabled=True):
    """
    创建 RAG 记忆实例（工厂函数）

    Args:
        novel_title: 小说标题
        storage_path: 存储路径
        enabled: 是否启用

    Returns:
        NovelRAGMemory or None
    """
    if not enabled:
        print("  ℹ️  RAG 功能已禁用")
        return None

    if not CHROMADB_AVAILABLE:
        print("  ⚠️  ChromaDB 未安装，RAG 功能不可用")
        return None

    try:
        return NovelRAGMemory(novel_title, storage_path)
    except Exception as e:
        print(f"  ⚠️  创建 RAG 失败: {str(e)[:50]}")
        return None
