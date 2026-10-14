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
    results = vector_store.similarity_search_with_relevance_scores(keyword, k=3)
    hits = []
    for document, relevance in results:
        score = float(relevance)
        if not 0.0 <= score <= 1.0:
            raise ValueError("검색 결과의 유사도 점수가 0~1 범위를 벗어났습니다.")
        source_id = document.metadata.get("source_id", "unknown")
        hits.append({"id": source_id,
                     "title": document.metadata.get("title", "manual"),
                     "excerpt": document.page_content,
                     "score": score,
                     "source": f"qdrant://{source_id}"})
    return hits
