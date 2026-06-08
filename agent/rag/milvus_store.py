"""
Milvus向量存储服务类
提供Milvus数据库的连接、文档存储和检索功能
"""
from langchain_milvus import Milvus
from langchain_core.documents import Document
from agent.utils.config_handler import milvus_conf
from agent.model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from agent.utils.path_tool import get_abs_path
from agent.utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from agent.utils.logger_handler import logger
from pymilvus import connections, Collection, utility
import os


class MilvusVectorStoreService:
    def __init__(self):
        self.host = milvus_conf["host"]
        self.port = milvus_conf["port"]
        self.collection_name = milvus_conf["collection_name"]
        self.dim = milvus_conf["dim"]
        self.top_k = milvus_conf["top_k"]
        
        # 连接Milvus
        self._connect()
        
        # 创建或获取集合
        self._create_collection()
        
        # 创建LangChain Milvus包装器
        self.vector_store = Milvus(
            collection_name=self.collection_name,
            embedding_function=embed_model,
            connection_args={"host": self.host, "port": self.port},
        )

        # 初始化文本分割器
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=milvus_conf.get("chunk_size", 200),
            chunk_overlap=milvus_conf.get("chunk_overlap", 20),
            separators=milvus_conf.get("separators", ["\n\n", "\n", ".", ",", "?", "！", "。", "，", "？", " "]),
            length_function=len,
        )

    def _connect(self):
        """连接Milvus服务器"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            logger.info(f"[Milvus] 成功连接到 Milvus: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"[Milvus] 连接失败: {str(e)}", exc_info=True)
            raise

    def _create_collection(self):
        """创建集合（如果不存在）"""
        try:
            if not utility.has_collection(self.collection_name):
                # 创建集合
                fields = [
                    {"name": "id", "type": "INT64", "is_primary": True, "auto_id": True},
                    {"name": "embedding", "type": "FLOAT_VECTOR", "dim": self.dim},
                    {"name": "content", "type": "VARCHAR", "max_length": 65535},
                    {"name": "source", "type": "VARCHAR", "max_length": 512},
                ]
                
                schema = {
                    "fields": fields,
                    "auto_id": True,
                    "primary_field": "id"
                }
                
                # 使用LangChain的Milvus会自动创建集合，这里先检查
                logger.info(f"[Milvus] 集合 {self.collection_name} 不存在，将在首次插入时自动创建")
            else:
                logger.info(f"[Milvus] 集合 {self.collection_name} 已存在")
        except Exception as e:
            logger.error(f"[Milvus] 创建集合失败: {str(e)}", exc_info=True)

    def get_retriever(self):
        """获取检索器"""
        return self.vector_store.as_retriever(search_kwargs={"k": self.top_k})

    def load_document(self, data_path: str = None):
        """
        从数据文件夹内读取数据文件，转为向量存入Milvus
        要计算文件的MD5做去重
        """
        if data_path is None:
            data_path = milvus_conf.get("data_path", "data")
        
        md5_store_path = get_abs_path(milvus_conf.get("md5_hex_store", "milvus_md5.txt"))

        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(md5_store_path):
                open(md5_store_path, "w", encoding="utf-8").close()
                return False
            
            with open(md5_store_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.strip() == md5_for_check:
                        return True
            return False

        def save_md5_hex(md5_for_check: str):
            with open(md5_store_path, "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str):
            if read_path.endswith(".txt"):
                return txt_loader(read_path)
            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)
            return []

        allowed_files = listdir_with_allowed_type(
            get_abs_path(data_path),
            tuple(milvus_conf.get("allow_knowledge_file_type", ["txt", "pdf"]))
        )

        for path in allowed_files:
            md5_hex = get_file_md5_hex(path)
            
            if check_md5_hex(md5_hex):
                logger.info(f"[Milvus] {path} 内容已存在，跳过")
                continue

            try:
                documents = get_file_documents(path)
                
                if not documents:
                    logger.warning(f"[Milvus] {path} 没有有效内容，跳过")
                    continue

                split_docs = self.spliter.split_documents(documents)
                
                if not split_docs:
                    logger.warning(f"[Milvus] {path} 分片后无有效内容，跳过")
                    continue

                self.vector_store.add_documents(split_docs)
                save_md5_hex(md5_hex)
                
                logger.info(f"[Milvus] {path} 加载成功")
            except Exception as e:
                logger.error(f"[Milvus] {path} 加载失败: {str(e)}", exc_info=True)
                continue

    def search(self, query: str, k: int = None):
        """
        搜索相似文档
        """
        if k is None:
            k = self.top_k
        
        retriever = self.get_retriever()
        return retriever.invoke(query)

    def get_collection_stats(self):
        """获取集合统计信息"""
        try:
            collection = Collection(self.collection_name)
            collection.load()
            stats = collection.num_entities
            collection.release()
            return {"count": stats}
        except Exception as e:
            logger.error(f"[Milvus] 获取统计信息失败: {str(e)}")
            return {"error": str(e)}

    def clear_collection(self):
        """清空集合"""
        try:
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                logger.info(f"[Milvus] 集合 {self.collection_name} 已删除")
        except Exception as e:
            logger.error(f"[Milvus] 清空集合失败: {str(e)}", exc_info=True)

    def disconnect(self):
        """断开连接"""
        try:
            connections.disconnect("default")
            logger.info("[Milvus] 连接已断开")
        except Exception as e:
            logger.error(f"[Milvus] 断开连接失败: {str(e)}")


if __name__ == '__main__':
    # 测试Milvus连接
    try:
        vs = MilvusVectorStoreService()
        print("Milvus连接成功")
        
        # 加载文档
        vs.load_document()
        
        # 测试搜索
        results = vs.search("人力资源")
        print(f"搜索结果数量: {len(results)}")
        for i, r in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(r.page_content[:100] + "..." if len(r.page_content) > 100 else r.page_content)
        
        # 获取统计
        stats = vs.get_collection_stats()
        print(f"\n集合统计: {stats}")
        
        vs.disconnect()
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
