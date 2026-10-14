"""Optional Qdrant-backed semantic retrieval; keyword mode remains available offline."""
import os
from app.knowledge import MANUALS, search_manual


def index_demo_documents() -> int:
    from langchain_core.documents import Document
    from langchain_openai import OpenAIEmbeddings
    from langchain_qdrant import QdrantVectorStore
    docs = [Document(page_content=body, metadata={"source_id": doc_id, "title": title})
            for doc_id, (title, body) in MANUALS.items()]
    QdrantVectorStore.from_documents(
        docs, embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        url=os.environ["QDRANT_URL"], collection_name="fictional_manuals")
    return len(docs)


def retrieve(keyword: str) -> list[dict]:
    if os.environ.get("SEARCH_MODE", "keyword") != "qdrant":
        return search_manual(keyword)
    from langchain_openai import OpenAIEmbeddings
    from langchain_qdrant import QdrantVectorStore
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        url=os.environ["QDRANT_URL"], collection_name="fictional_manuals")
    return [{"id": d.metadata.get("source_id", "unknown"),
             "title": d.metadata.get("title", "manual"),
             "excerpt": d.page_content, "score": 1.0,
             "source": f"qdrant://{d.metadata.get('source_id', 'unknown')}"}
            for d in vector_store.similarity_search(keyword, k=3)]
