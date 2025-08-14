from typing import List

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings

settings = get_settings()

class VectorDB:
    def __init__(self):
        self.pc = Pinecone(
            api_key=settings.pinecone_api_key,
        )

        existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]
        index_name = settings.pinecone_index_name
        
        if index_name not in existing_indexes:
            self.pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                deletion_protection="enabled",  # Defaults to "disabled"
            )

        index = self.pc.Index(index_name)
        self.vector_store = PineconeVectorStore(index=index, embedding=OpenAIEmbeddings())    

    def add_documents(self, documents: list):
        self.vector_store.add_documents(documents)

    def delete_document(self, doc_ids: List[str]):
        self.vector_store.delete(doc_ids)

    def search(self, query: str, top_k: int = 5):
        return self.vector_store.similarity_search(query, k=top_k)

vdb = VectorDB()