import pandas as pd
from llama_index.core import VectorStoreIndex, Document, SimpleKeywordTableIndex
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.retrievers import QueryFusionRetriever

import chromadb
import os
import pickle

# 1. OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] =  ''


# 2. Excel 파일에서 데이터 로드
file_path = 'data/final.xlsx'
data = pd.read_excel(file_path)

# 3. 내용 컬럼을 기반으로 Document 생성
documents = []
for index, row in data.iterrows():
    content = row['내용']
    title = row['제목']
    link = row['링크']
    
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

# 8. 키워드 인덱스를 로드할지 아니면 새로 생성할지 결정
try:
    # 기존 키워드 인덱스를 pickle로부터 로드
    with open('keyword_index.pkl', 'rb') as f:
        keyword_index = pickle.load(f)
    print("키워드 인덱스 로드 완료.")
except FileNotFoundError:
    # 키워드 인덱스가 없으면 새로 생성
    print("키워드 인덱스가 없어서 새로 생성합니다.")
    keyword_index = SimpleKeywordTableIndex.from_documents(documents)
    
    # 9. 키워드 인덱스를 pickle로 디스크에 저장
    with open('keyword_index.pkl', 'wb') as f:
        pickle.dump(keyword_index, f)
    print("키워드 인덱스 저장 완료.")

# 10. 문서를 노드로 변환
parser = SimpleNodeParser()
nodes = parser.get_nodes_from_documents(documents)

# 11. BM25Retriever 생성 (노드를 사용)
bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=2)

# 12. 벡터 인덱스 기반 검색 설정
vector_retriever = vector_index.as_retriever(similarity_top_k=2)

# 13. QueryFusionRetriever를 사용하여 하이브리드 쿼리 엔진 생성
fusion_retriever = QueryFusionRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    retriever_weights=[0.5, 0.5],  # 가중치 조정 가능
    similarity_top_k=5,  # 상위 5개의 결과를 반환
    num_queries=1,  # 추가 쿼리 생성 비활성화
)

# 14. 예시 질문 처리
query = "연인을 어디서 찾을 수 있을까?"
retrieved_nodes = fusion_retriever.retrieve(query)

# 15. 결과 출력
for node in retrieved_nodes:
    print(node.get_text())
