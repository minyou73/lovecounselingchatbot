import pandas as pd
from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.core.node_parser import SimpleNodeParser  # 노드 파서 추가
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
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

# 4. 문서를 청크로 나누기 위한 노드 파서 설정 (기본적으로 문장 단위로 분할)
parser = SimpleNodeParser()

# 문서에서 노드(청크)로 분할
nodes = parser.get_nodes_from_documents(documents)

# 5. OpenAI 임베딩 모델 명시적 설정
embedding_model = OpenAIEmbedding(model="text-embedding-ada-002")

# 6. Chroma 클라이언트 초기화 (데이터를 저장할 경로 설정)
client = chromadb.PersistentClient(path="./chroma_db")  # 로컬 데이터 저장 경로 지정

# 7. Chroma 컬렉션 생성
chroma_collection = client.get_or_create_collection("youtube_data")

# 8. Chroma를 벡터 스토어로 사용
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 9. 벡터 인덱스 생성 (Chroma에 저장), 분할된 노드를 임베딩 모델과 함께 전달
vector_index = VectorStoreIndex(
    nodes, storage_context=storage_context, embed_model=embedding_model
)

# 10. 검색 엔진 생성
query_engine = vector_index.as_query_engine()

# 11. 예시 질문 처리
response = query_engine.query("연인을 어디서 찾을 수 있을까?")
print(response)
