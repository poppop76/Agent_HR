"""
记忆管理系统 - 混合存储版
结合 MySQL（结构化存储）和 Milvus（向量存储）实现长期记忆
"""
import json
import redis
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from db.database import Base, get_db
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import uuid

logger = logging.getLogger(__name__)

# ========== 数据库模型 ==========

class ConversationMemory(Base):
    """长期记忆：对话记录表"""
    __tablename__ = "conversation_memory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)  # 会话 ID
    memory_id = Column(String(64), nullable=False, unique=True)  # 唯一标识，用于关联 Milvus
    user_id = Column(Integer, nullable=True)  # 用户 ID（可选）
    role = Column(String(20), nullable=False)  # user 或 assistant
    content = Column(Text, nullable=False)  # 对话内容
    keywords = Column(JSON, default=list)  # 提取的关键词列表
    summary = Column(Text, nullable=True)  # 对话摘要
    created_at = Column(DateTime, default=datetime.now, index=True)  # 创建时间
    compressed = Column(Integer, default=0)  # 是否被压缩（0:否，1:是）
    parent_id = Column(Integer, nullable=True)  # 父对话 ID（用于对话树）
    
    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
        Index('idx_memory_id', 'memory_id'),
    )


class ConversationSession(Base):
    """会话元信息表"""
    __tablename__ = "conversation_session"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=True)
    title = Column(String(255), nullable=True)  # 会话标题（从第一段对话生成）
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    message_count = Column(Integer, default=0)  # 消息数量
    is_active = Column(Integer, default=1)  # 是否活跃
    
    __table_args__ = (
        Index('idx_user_active', 'user_id', 'is_active'),
    )


# ========== Milvus 向量存储 ==========

class MilvusMemory:
    """
    Milvus 向量存储管理器
    用于存储对话的向量嵌入，支持语义相似度搜索
    """
    
    def __init__(self, collection_name: str = None):
        from core.config import settings
        self.collection_name = collection_name or settings.MILVUS_COLLECTION
        self.client = None
        self._init_milvus()
    
    def _init_milvus(self):
        """初始化 Milvus 连接"""
        try:
            from pymilvus import MilvusClient, connections, Collection, utility
            from core.config import settings
            
            # 尝试获取现有的 Milvus 客户端（如果项目中有）
            try:
                from agent.rag.milvus_store import get_milvus_client
                self.client = get_milvus_client()
                logger.info("[MilvusMemory] 成功连接到 Milvus（复用现有客户端）")
            except ImportError:
                # agent.rag.milvus_store 模块不存在，直接创建新客户端
                logger.info("[MilvusMemory] 创建新的 Milvus 客户端连接")
                self.client = MilvusClient(uri=settings.MILVUS_URI)
            except Exception as e:
                # 其他错误，创建新客户端
                logger.warning(f"[MilvusMemory] 获取现有客户端失败: {e}，创建新连接")
                self.client = MilvusClient(uri=settings.MILVUS_URI)
            
            # 创建集合（如果不存在）
            self._create_collection_if_not_exists()
            
        except ImportError:
            logger.warning("[MilvusMemory] pymilvus 客户端未安装，请运行: pip install pymilvus")
            self.client = None
        except Exception as e:
            logger.error(f"[MilvusMemory] Milvus 初始化失败: {e}")
            self.client = None
    
    def _create_collection_if_not_exists(self):
        """创建集合（如果不存在）"""
        if not self.client:
            return
            
        try:
            from pymilvus import MilvusClient, DataType
            
            if not self.client.has_collection(self.collection_name):
                # 创建集合
                schema = MilvusClient.create_schema(
                    auto_id=False,  # 使用自定义主键
                    enable_dynamic_field=True
                )
                schema.add_field(field_name="memory_id", datatype=DataType.VARCHAR, max_length=64, is_primary=True)
                schema.add_field(field_name="session_id", datatype=DataType.VARCHAR, max_length=64)
                schema.add_field(field_name="role", datatype=DataType.VARCHAR, max_length=20)
                schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=4000)
                schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=384)
                
                index_params = self.client.prepare_index_params()
                index_params.add_index(
                    field_name="embedding",
                    index_type="IVF_FLAT",
                    metric_type="L2",
                    params={"nlist": 1024}
                )
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    schema=schema,
                    index_params=index_params
                )
                logger.info(f"[MilvusMemory] 创建集合: {self.collection_name}")
            else:
                logger.info(f"[MilvusMemory] 集合已存在: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"[MilvusMemory] 创建集合失败: {e}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取文本的向量嵌入"""
        try:
            # 提前设置环境变量（在导入 HuggingFace 库之前）
            import os
            os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
            os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
            
            # 延迟导入，确保环境变量已设置
            from huggingface_hub import snapshot_download
            
            # 先尝试下载模型到本地缓存
            try:
                model_path = snapshot_download(
                    repo_id="sentence-transformers/all-MiniLM-L6-v2",
                    local_dir=None,  # 使用默认缓存目录
                    resume_download=True
                )
            except Exception as e:
                logger.warning(f"[MilvusMemory] 模型下载失败，使用默认路径: {e}")
                model_path = "sentence-transformers/all-MiniLM-L6-v2"
            
            # 尝试新版 langchain
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
            except ImportError:
                # 兼容旧版 langchain
                from langchain.embeddings import HuggingFaceEmbeddings
            
            embeddings = HuggingFaceEmbeddings(
                model_name=model_path,
                model_kwargs={"device": "cpu"}
            )
            return embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"[MilvusMemory] 获取嵌入失败: {e}")
            return []
    
    def insert_vector(self, memory_id: str, session_id: str, role: str, content: str):
        """
        插入对话向量到 Milvus
        :param memory_id: 对话唯一标识
        :param session_id: 会话 ID
        :param role: 角色
        :param content: 内容
        """
        if not self.client:
            return
        
        try:
            embedding = self._get_embedding(content)
            if not embedding:
                logger.warning("[MilvusMemory] 无法获取嵌入，跳过向量插入")
                return
            
            data = [{
                "memory_id": memory_id,
                "session_id": session_id,
                "role": role,
                "content": content[:4000],
                "embedding": embedding
            }]
            
            self.client.insert(
                collection_name=self.collection_name,
                data=data
            )
            logger.debug(f"[MilvusMemory] 插入向量成功: memory_id={memory_id}")
            
        except Exception as e:
            logger.error(f"[MilvusMemory] 插入向量失败: {e}")
    
    def search_similar(self, query_text: str, session_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        语义相似度搜索
        :param query_text: 查询文本
        :param session_id: 会话 ID（可选）
        :param limit: 返回数量限制
        :return: 匹配结果列表
        """
        if not self.client:
            return []
        
        try:
            embedding = self._get_embedding(query_text)
            if not embedding:
                return []
            
            # 构建搜索参数
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }
            
            # 构建过滤条件
            filter_expr = None
            if session_id:
                filter_expr = f"session_id == '{session_id}'"
            
            results = self.client.search(
                collection_name=self.collection_name,
                data=[embedding],
                limit=limit,
                filter=filter_expr,
                search_params=search_params,
                output_fields=["memory_id", "session_id", "role", "content"]
            )
            
            # 处理结果
            matched = []
            for hit in results[0]:
                entity = hit["entity"]
                matched.append({
                    "memory_id": entity["memory_id"],
                    "session_id": entity["session_id"],
                    "role": entity["role"],
                    "content": entity["content"],
                    "similarity_score": 1 - hit["distance"] / 2,  # 转换为相似度分数
                    "source": "milvus"
                })
            
            logger.debug(f"[MilvusMemory] 语义搜索完成，找到 {len(matched)} 条结果")
            return matched
            
        except Exception as e:
            logger.error(f"[MilvusMemory] 搜索失败: {e}")
            return []


# ========== 短期记忆（Redis） ==========

class ShortTermMemory:
    """
    短期记忆管理器
    使用 Redis 存储最近的对话上下文（默认 5 条）
    """
    
    def __init__(self, redis_client, max_contexts: int = 5):
        """
        :param redis_client: Redis 客户端
        :param max_contexts: 最大存储的上下文数量
        """
        self.redis = redis_client
        self.max_contexts = max_contexts
        self.context_ttl = 3600  # 1 小时过期
    
    def _get_context_key(self, session_id: str) -> str:
        """获取上下文存储的 key"""
        return f"agent:memory:short:{session_id}:contexts"
    
    def _get_keywords_key(self, session_id: str) -> str:
        """获取关键词存储的 key"""
        return f"agent:memory:short:{session_id}:keywords"
    
    def add_context(self, session_id: str, role: str, content: str, keywords: List[str] = None):
        """
        添加一条对话上下文
        :param session_id: 会话 ID
        :param role: 角色（user/assistant）
        :param content: 对话内容
        :param keywords: 提取的关键词
        """
        context_key = self._get_context_key(session_id)
        keywords_key = self._get_keywords_key(session_id)
        
        context_data = {
            "role": role,
            "content": content,
            "keywords": keywords or [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 使用 list 存储上下文（保持顺序）
        pipe = self.redis.pipeline()
        pipe.rpush(context_key, json.dumps(context_data, ensure_ascii=False))
        
        # 保持列表长度在 max_contexts 以内
        pipe.ltrim(context_key, -self.max_contexts, -1)
        
        # 设置过期时间
        pipe.expire(context_key, self.context_ttl)
        pipe.expire(keywords_key, self.context_ttl)
        
        pipe.execute()
        
        logger.debug(f"[ShortTermMemory] 添加上下文到 session={session_id}, role={role}")
    
    def get_contexts(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取所有短期记忆上下文
        :param session_id: 会话 ID
        :return: 上下文列表
        """
        context_key = self._get_context_key(session_id)
        contexts_raw = self.redis.lrange(context_key, 0, -1)
        
        contexts = []
        for ctx in contexts_raw:
            try:
                contexts.append(json.loads(ctx))
            except:
                logger.warning(f"[ShortTermMemory] 解析上下文失败：{ctx[:50]}")
        
        return contexts
    
    def search_by_keywords(self, session_id: str, query_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        根据关键词搜索相关上下文
        :param session_id: 会话 ID
        :param query_keywords: 查询关键词列表
        :return: 匹配的上下文列表
        """
        contexts = self.get_contexts(session_id)
        matched = []
        
        for ctx in contexts:
            ctx_keywords = set(ctx.get("keywords", []))
            query_set = set(query_keywords)
            
            # 计算关键词重合度
            intersection = ctx_keywords & query_set
            if intersection:
                ctx["match_score"] = len(intersection)
                matched.append(ctx)
        
        # 按匹配度排序
        matched.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        logger.debug(f"[ShortTermMemory] 关键词搜索：query={query_keywords}, matched={len(matched)}")
        return matched
    
    def get_recent_keywords(self, session_id: str, limit: int = 10) -> List[str]:
        """
        获取最近对话的关键词
        :param session_id: 会话 ID
        :param limit: 最大关键词数量
        :return: 关键词列表
        """
        contexts = self.get_contexts(session_id)
        all_keywords = []
        
        for ctx in contexts:
            keywords = ctx.get("keywords", [])
            all_keywords.extend(keywords)
        
        # 去重并限制数量
        unique_keywords = list(set(all_keywords))[:limit]
        
        logger.debug(f"[ShortTermMemory] 获取最近关键词：session={session_id}, keywords={unique_keywords}")
        return unique_keywords
    
    def clear_session(self, session_id: str):
        """清空会话的短期记忆"""
        context_key = self._get_context_key(session_id)
        keywords_key = self._get_keywords_key(session_id)
        self.redis.delete(context_key, keywords_key)
        logger.debug(f"[ShortTermMemory] 清空 session={session_id}")


# ========== 长期记忆（MySQL + Milvus 混合） ==========

class LongTermMemory:
    """
    长期记忆管理器
    结合 MySQL（结构化存储）和 Milvus（向量存储）实现混合记忆
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.milvus = MilvusMemory()
    
    def _get_db_session(self) -> Session:
        """获取数据库会话"""
        return next(get_db())
    
    def save_conversation(self, session_id: str, role: str, content: str, 
                         keywords: List[str] = None, user_id: int = None,
                         parent_id: int = None, summary: str = None):
        """
        保存对话到长期记忆（异步）
        :param session_id: 会话 ID
        :param role: 角色
        :param content: 内容
        :param keywords: 关键词
        :param user_id: 用户 ID
        :param parent_id: 父对话 ID
        :param summary: 对话摘要
        """
        # 生成唯一的 memory_id
        memory_id = str(uuid.uuid4())
        
        def _save():
            try:
                db = self._get_db_session()
                
                # 创建对话记录
                memory = ConversationMemory(
                    session_id=session_id,
                    memory_id=memory_id,
                    user_id=user_id,
                    role=role,
                    content=content,
                    keywords=keywords or [],
                    summary=summary,
                    parent_id=parent_id
                )
                
                db.add(memory)
                
                # 更新会话元信息
                session = db.query(ConversationSession).filter_by(session_id=session_id).first()
                if not session:
                    session = ConversationSession(
                        session_id=session_id,
                        user_id=user_id,
                        title=content[:50] if role == "user" else None,
                        message_count=1
                    )
                    db.add(session)
                else:
                    session.message_count += 1
                    session.updated_at = datetime.now()
                    if not session.title and role == "user":
                        session.title = content[:50]
                
                db.commit()
                
                logger.debug(f"[LongTermMemory] 保存对话到 MySQL: session={session_id}, memory_id={memory_id}")
                
            except Exception as e:
                logger.error(f"[LongTermMemory] MySQL 保存失败：{str(e)}")
                db.rollback()
            finally:
                db.close()
        
        # 异步保存到 MySQL
        self.executor.submit(_save)
        
        # 异步保存到 Milvus（向量存储）
        def _save_to_milvus():
            self.milvus.insert_vector(memory_id, session_id, role, content)
        
        self.executor.submit(_save_to_milvus)
    
    def search_by_keywords(self, session_id: str, query_keywords: List[str], 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        根据关键词搜索长期记忆（MySQL）
        :param session_id: 会话 ID（可传 None 搜索所有会话）
        :param query_keywords: 查询关键词
        :param limit: 返回数量限制
        :return: 匹配的对话列表
        """
        db = self._get_db_session()
        try:
            query = db.query(ConversationMemory)
            
            if session_id:
                query = query.filter(ConversationMemory.session_id == session_id)
            
            # 获取所有记录（简化实现，实际可使用全文索引优化）
            memories = query.order_by(
                ConversationMemory.created_at.desc()
            ).limit(limit * 2).all()  # 获取更多结果用于过滤
            
            results = []
            for mem in memories:
                # 计算关键词匹配度
                mem_keywords = set(mem.keywords or [])
                query_set = set(query_keywords)
                match_score = len(mem_keywords & query_set)
                
                if match_score > 0:
                    results.append({
                        "memory_id": mem.memory_id,
                        "session_id": mem.session_id,
                        "role": mem.role,
                        "content": mem.content,
                        "keywords": mem.keywords,
                        "summary": mem.summary,
                        "created_at": mem.created_at.isoformat(),
                        "match_score": match_score,
                        "source": "mysql"
                    })
            
            # 按匹配度排序
            results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            
            logger.debug(f"[LongTermMemory] MySQL关键词搜索：query={query_keywords}, matched={len(results)}")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"[LongTermMemory] MySQL搜索失败：{str(e)}")
            return []
        finally:
            db.close()
    
    def search_semantic(self, query_text: str, session_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        语义相似度搜索（Milvus）
        :param query_text: 查询文本
        :param session_id: 会话 ID（可选）
        :param limit: 返回数量限制
        :return: 匹配的对话列表
        """
        return self.milvus.search_similar(query_text, session_id, limit)
    
    def hybrid_search(self, query_text: str, query_keywords: List[str], 
                     session_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        混合搜索：结合关键词搜索（MySQL）和语义搜索（Milvus）
        :param query_text: 查询文本（用于语义搜索）
        :param query_keywords: 查询关键词（用于关键词搜索）
        :param session_id: 会话 ID（可选）
        :param limit: 返回数量限制
        :return: 综合匹配结果
        """
        # 并行执行两种搜索
        keyword_results = self.search_by_keywords(session_id, query_keywords, limit)
        semantic_results = self.search_semantic(query_text, session_id, limit)
        
        # 合并结果（去重）
        all_results = keyword_results + semantic_results
        
        # 去重（基于 memory_id 或 content）
        seen = set()
        unique_results = []
        for result in all_results:
            identifier = result.get("memory_id", result.get("content", "")[:100])
            if identifier not in seen:
                seen.add(identifier)
                unique_results.append(result)
        
        # 综合排序：关键词匹配度 * 0.4 + 语义相似度 * 0.6
        for result in unique_results:
            keyword_score = result.get("match_score", 0) / 5  # 归一化到 0-1
            semantic_score = result.get("similarity_score", 0)
            result["hybrid_score"] = keyword_score * 0.4 + semantic_score * 0.6
        
        # 按综合分数排序
        unique_results.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
        
        logger.debug(f"[LongTermMemory] 混合搜索完成，共 {len(unique_results)} 条结果")
        return unique_results[:limit]
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取会话历史记录
        :param session_id: 会话 ID
        :param limit: 返回数量限制
        :return: 历史对话列表
        """
        db = self._get_db_session()
        try:
            memories = db.query(ConversationMemory).filter_by(
                session_id=session_id
            ).order_by(
                ConversationMemory.created_at.asc()
            ).limit(limit).all()
            
            return [
                {
                    "id": mem.id,
                    "memory_id": mem.memory_id,
                    "role": mem.role,
                    "content": mem.content,
                    "keywords": mem.keywords,
                    "summary": mem.summary,
                    "created_at": mem.created_at.isoformat(),
                    "compressed": mem.compressed
                }
                for mem in memories
            ]
        except Exception as e:
            logger.error(f"[LongTermMemory] 获取历史失败：{str(e)}")
            return []
        finally:
            db.close()
    
    def get_active_sessions(self, user_id: int = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取活跃会话列表
        :param user_id: 用户 ID
        :param limit: 返回数量限制
        :return: 会话列表
        """
        db = self._get_db_session()
        try:
            query = db.query(ConversationSession).filter_by(is_active=1)
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            sessions = query.order_by(
                ConversationSession.updated_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "session_id": s.session_id,
                    "title": s.title,
                    "message_count": s.message_count,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat()
                }
                for s in sessions
            ]
        except Exception as e:
            logger.error(f"[LongTermMemory] 获取会话列表失败：{str(e)}")
            return []
        finally:
            db.close()
    
    def compress_conversation(self, memory_id: int, compressed_content: str):
        """
        压缩对话记录
        :param memory_id: 对话 ID
        :param compressed_content: 压缩后的内容
        """
        db = self._get_db_session()
        try:
            memory = db.query(ConversationMemory).filter_by(id=memory_id).first()
            if memory:
                memory.compressed = 1
                memory.summary = compressed_content
                db.commit()
                logger.debug(f"[LongTermMemory] 压缩对话 id={memory_id}")
        except Exception as e:
            logger.error(f"[LongTermMemory] 压缩失败：{str(e)}")
            db.rollback()
        finally:
            db.close()


# ========== 关键词提取 ==========

class KeywordExtractor:
    """关键词提取器"""
    
    def __init__(self):
        # 停用词表（可根据需要扩展）
        self.stopwords = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
            "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
            "你", "会", "着", "没有", "看", "好", "自己", "这", "那",
            "什么", "怎么", "吗", "呢", "啊", "吧", "哦", "嗯"
        }
    
    def extract(self, text: str, top_k: int = 5) -> List[str]:
        """
        从文本中提取关键词
        简化版：使用分词 + 词频统计
        :param text: 输入文本
        :param top_k: 返回前 K 个关键词
        :return: 关键词列表
        """
        import re
        
        # 提取中文词语（2-4 个字）
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        
        # 过滤停用词
        filtered_words = [w for w in words if w not in self.stopwords]
        
        # 词频统计
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按词频排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        keywords = [word for word, freq in sorted_words[:top_k]]
        
        return keywords
    
    def extract_batch(self, texts: List[str], top_k: int = 10) -> List[str]:
        """
        批量提取关键词
        :param texts: 文本列表
        :param top_k: 返回前 K 个关键词
        :return: 关键词列表
        """
        all_words = []
        for text in texts:
            all_words.extend(self.extract(text, top_k=top_k))
        
        # 去重
        return list(set(all_words))


# ========== 上下文压缩 ==========

class ContextCompressor:
    """上下文压缩器"""
    
    def __init__(self, max_length: int = 4000, compression_ratio: float = 0.7):
        """
        :param max_length: 最大上下文长度
        :param compression_ratio: 压缩比例
        """
        self.max_length = max_length
        self.compression_ratio = compression_ratio
    
    def need_compress(self, contexts: List[Dict[str, Any]]) -> bool:
        """
        判断是否需要压缩
        :param contexts: 上下文列表
        :return: 是否需要压缩
        """
        total_length = sum(len(ctx.get("content", "")) for ctx in contexts)
        return total_length > self.max_length
    
    def compress(self, contexts: List[Dict[str, Any]], 
                 extractor: KeywordExtractor) -> List[Dict[str, Any]]:
        """
        压缩上下文
        策略：保留关键词丰富的对话，压缩或移除不重要的对话
        :param contexts: 上下文列表
        :param extractor: 关键词提取器
        :return: 压缩后的上下文列表
        """
        if not self.need_compress(contexts):
            return contexts
        
        logger.debug(f"[ContextCompressor] 开始压缩，原始长度={len(contexts)}")
        
        # 计算每个上下文的重要性（基于关键词数量）
        scored_contexts = []
        for ctx in contexts:
            keywords = ctx.get("keywords", [])
            score = len(keywords)
            scored_contexts.append((ctx, score))
        
        # 按重要性排序
        scored_contexts.sort(key=lambda x: x[1], reverse=True)
        
        # 保留最重要的部分
        keep_count = max(3, int(len(contexts) * self.compression_ratio))
        kept = scored_contexts[:keep_count]
        
        # 压缩保留的上下文（如果仍然太长）
        compressed_contexts = []
        for ctx, score in kept:
            content = ctx.get("content", "")
            if len(content) > 500:
                # 简单截断（可优化为使用 LLM 摘要）
                compressed_content = content[:500] + "..."
                ctx["content"] = compressed_content
                ctx["compressed"] = True
            compressed_contexts.append(ctx)
        
        logger.debug(f"[ContextCompressor] 压缩后长度={len(compressed_contexts)}")
        return compressed_contexts


# ========== 记忆管理器（统一接口） ==========

class MemoryManager:
    """
    记忆管理器
    统一管理短期记忆和长期记忆的切换
    长期记忆采用 MySQL + Milvus 混合架构
    支持Query改写功能
    """
    
    def __init__(self, redis_client):
        """
        :param redis_client: Redis 客户端
        """
        self.short_term = ShortTermMemory(redis_client, max_contexts=5)
        self.long_term = LongTermMemory()
        self.keyword_extractor = KeywordExtractor()
        self.context_compressor = ContextCompressor(max_length=4000)
        
        # 初始化Query改写器
        try:
            from agent.query_rewriter import get_query_rewriter
            self.query_rewriter = get_query_rewriter()
            logger.info("[MemoryManager] Query改写器初始化成功")
        except Exception as e:
            logger.warning(f"[MemoryManager] Query改写器初始化失败: {e}")
            self.query_rewriter = None
    
    def rewrite_query(self, original_query: str, session_context: Optional[dict] = None) -> str:
        """
        改写用户查询，使其更精准
        
        Args:
            original_query: 用户原始问题
            session_context: 会话上下文信息
            
        Returns:
            改写后的查询语句
        """
        if not self.query_rewriter:
            return original_query
        
        try:
            # 获取历史关键词作为上下文
            if not session_context:
                session_context = {}
            
            # 提取最近对话的关键词
            recent_keywords = self.short_term.get_recent_keywords(
                session_context.get('session_id', ''), 
                limit=10
            )
            session_context['history_keywords'] = recent_keywords
            
            # 进行Query改写
            rewritten_query = self.query_rewriter.rewrite_with_context_detection(
                original_query, 
                session_context
            )
            
            logger.info(f"[MemoryManager] Query改写: '{original_query}' -> '{rewritten_query}'")
            return rewritten_query
            
        except Exception as e:
            logger.error(f"[MemoryManager] Query改写失败: {e}")
            return original_query
    
    def add_message(self, session_id: str, role: str, content: str, 
                   user_id: int = None, parent_id: int = None):
        """
        添加消息到记忆系统
        :param session_id: 会话 ID
        :param role: 角色
        :param content: 内容
        :param user_id: 用户 ID
        :param parent_id: 父对话 ID
        """
        # 提取关键词
        keywords = self.keyword_extractor.extract(content, top_k=5)
        
        # 添加到短期记忆
        self.short_term.add_context(session_id, role, content, keywords)
        
        # 异步保存到长期记忆（MySQL + Milvus）
        self.long_term.save_conversation(
            session_id=session_id,
            role=role,
            content=content,
            keywords=keywords,
            user_id=user_id,
            parent_id=parent_id
        )
        
        logger.info(f"[MemoryManager] 添加消息：session={session_id}, role={role}, keywords={keywords}")
    
    def get_context_for_llm(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取用于 LLM 的上下文
        优先使用短期记忆，如果不足则从长期记忆补充
        :param session_id: 会话 ID
        :return: 上下文列表
        """
        # 获取短期记忆
        short_contexts = self.short_term.get_contexts(session_id)
        
        # 检查是否需要压缩
        if self.context_compressor.need_compress(short_contexts):
            short_contexts = self.context_compressor.compress(
                short_contexts, 
                self.keyword_extractor
            )
        
        # 如果短期记忆不足，从长期记忆补充
        if len(short_contexts) < 5:
            long_contexts = self.long_term.get_session_history(session_id, limit=10)
            # 合并（长期记忆在前）
            short_contexts = long_contexts + short_contexts
        
        # 转换为 LLM 格式
        llm_context = []
        for ctx in short_contexts:
            llm_context.append({
                "role": ctx["role"],
                "content": ctx["content"]
            })
        
        return llm_context
    
    def search_memory(self, session_id: str, query: str, 
                     use_long_term: bool = True, use_semantic: bool = True) -> List[Dict[str, Any]]:
        """
        搜索记忆（支持关键词搜索和语义搜索）
        :param session_id: 会话 ID
        :param query: 查询文本
        :param use_long_term: 是否搜索长期记忆
        :param use_semantic: 是否使用语义搜索（Milvus）
        :return: 搜索结果
        """
        # 提取查询关键词
        keywords = self.keyword_extractor.extract(query, top_k=5)
        
        # 搜索短期记忆
        short_results = self.short_term.search_by_keywords(session_id, keywords)
        
        # 搜索长期记忆
        long_results = []
        if use_long_term:
            if use_semantic:
                # 使用混合搜索（关键词 + 语义）
                long_results = self.long_term.hybrid_search(query, keywords, session_id, limit=10)
            else:
                # 仅使用关键词搜索
                long_results = self.long_term.search_by_keywords(session_id, keywords, limit=10)
        
        # 合并结果
        all_results = short_results + long_results
        
        # 去重（基于 content）
        seen = set()
        unique_results = []
        for result in all_results:
            content = result.get("content", "")
            if content not in seen:
                seen.add(content)
                unique_results.append(result)
        
        logger.info(f"[MemoryManager] 搜索记忆：query={query[:30]}, results={len(unique_results)}")
        return unique_results
    
    def get_session_list(self, user_id: int = None) -> List[Dict[str, Any]]:
        """
        获取会话列表
        :param user_id: 用户 ID
        :return: 会话列表
        """
        return self.long_term.get_active_sessions(user_id, limit=20)
    
    def switch_session(self, old_session_id: str, new_session_id: str, user_id: int = None):
        """
        切换会话
        :param old_session_id: 原会话 ID
        :param new_session_id: 新会话 ID
        :param user_id: 用户 ID
        """
        # 清空短期记忆
        self.short_term.clear_session(old_session_id)
        
        logger.info(f"[MemoryManager] 切换会话：{old_session_id} -> {new_session_id}")
    
    def resume_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        恢复历史会话
        :param session_id: 会话 ID
        :return: 历史对话列表
        """
        return self.long_term.get_session_history(session_id, limit=50)
