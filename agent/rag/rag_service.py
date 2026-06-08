"""
总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
使用 Milvus 向量数据库
"""
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from agent.rag.milvus_store import MilvusVectorStoreService
from agent.utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from agent.model.factory import chat_model


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


class RagSummarizeService(object):
    def __init__(self):
        # 直接使用 Milvus 向量存储
        self.vector_store = MilvusVectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        """
        执行RAG总结
        :param query: 用户查询
        :return: 总结结果
        """
        context_docs = self.retriever_docs(query)

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】: 参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )

    def load_documents(self, data_path: str = None):
        """
        加载文档到 Milvus
        :param data_path: 数据路径
        """
        self.vector_store.load_document(data_path)

    def get_stats(self):
        """获取 Milvus 集合统计信息"""
        return self.vector_store.get_collection_stats()


if __name__ == '__main__':
    rag = RagSummarizeService()
    print("使用 Milvus 向量数据库")
    
    # 加载文档
    rag.load_documents()
    
    # 测试搜索
    result = rag.rag_summarize("人力资源管理")
    print("\n总结结果:")
    print(result)
