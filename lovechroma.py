import pandas as pd
from llama_index.core import VectorStoreIndex, Document, SimpleKeywordTableIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.indices.vector_store.base import VectorStoreIndex

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
import os

# 1. OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = '

# 2. Excel 파일에서 데이터 로드
file_path = 'data/final.xlsx'
data = pd.read_excel(file_path)

# 3. 내용 컬럼을 기반으로 Document 생성
documents = []
for index, row in data.iterrows():
    content = row['내용']  # 내용 컬럼에서 데이터를 가져옴
    title = row['제목']    # 제목을 메타데이터로 사용할 수 있음
    link = row['링크']     # 링크를 메타데이터로 추가
    
    # Document에 텍스트와 메타데이터 추가
    doc_text = f"Content: {content}"
    metadata = {"title": title, "link": link}
    
    # 문서 객체 생성
    documents.append(Document(text=doc_text, metadata=metadata))

# 4. Chroma 클라이언트 초기화 (기존 데이터가 저장된 경로 지정)
client = chromadb.PersistentClient(path="./chroma_db")

# 5. 기존 Chroma 컬렉션 불러오기
chroma_collection = client.get_or_create_collection("youtube_data")

# 6. Chroma를 벡터 스토어로 사용
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 7. 기존 벡터 인덱스 로드 (새로운 임베딩을 하지 않고 기존 임베딩 사용)
vector_index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store, storage_context=storage_context
)

# 8. 키워드 인덱스 생성 (BM25 기반 키워드 검색용)
keyword_index = SimpleKeywordTableIndex.from_documents(documents)

# 9. BM25Retriever 생성 (문서 노드 사용)
nodes = keyword_index.get_nodes()
bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=2)

# 10. 벡터 인덱스 기반 검색 설정
vector_retriever = VectorIndexRetriever(index=vector_index)

# 11. 두 리트리버를 결합한 하이브리드 쿼리 엔진 생성
hybrid_query_engine = RetrieverQueryEngine.from_retrievers(
    retrievers=[bm25_retriever, vector_retriever],
    retriever_weights=[0.5, 0.5]  # 가중치 조정 가능
)

# 12. 예시 질문 처리
response = hybrid_query_engine.query("연인을 어디서 찾을 수 있을까?")
print(response)
