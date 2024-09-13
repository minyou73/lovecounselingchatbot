import pandas as pd
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.llms.openai import OpenAI
import chromadb
import logging

import os
os.environ["OPENAI_API_KEY"] = '


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전역 변수
fusion_retriever = None
chat_engine = None

def initialize_chat_engine():
    global fusion_retriever, chat_engine
    
    logger.info("Initializing chat engine...")

    # 현재 파일의 디렉토리 경로 가져오기
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 'data/final.xlsx' 파일의 절대 경로 생성
    file_path = os.path.join(current_dir, 'data', 'final.xlsx')

    # Excel 파일에서 데이터 로드
    data = pd.read_excel(file_path)

    # Document 생성
    documents = []
    for index, row in data.iterrows():
        content = row['내용']
        title = row['제목']
        link = row['링크']
        
        doc_text = f"Content: {content}"
        metadata = {"title": title, "link": link}
        
        documents.append(Document(text=doc_text, metadata=metadata))
    logger.info(f"Total documents loaded: {len(documents)}")

    # Chroma 설정
    chroma_db_path = os.path.join(current_dir, "chroma_db")
    client = chromadb.PersistentClient(path=chroma_db_path)
    chroma_collection = client.get_or_create_collection("youtube_data")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, storage_context=storage_context
    )

    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(documents)

    bm25_retriever = BM25Retriever.from_defaults(
        nodes=nodes,
        similarity_top_k=2
    )

    vector_retriever = vector_index.as_retriever(similarity_top_k=2)

    fusion_retriever = QueryFusionRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        retriever_weights=[0.5, 0.5],
        similarity_top_k=5,
        num_queries=1
    )

    llm = OpenAI(model="gpt-3.5-turbo")

    chat_engine = vector_index.as_chat_engine(
        llm=llm,
        chat_mode="condense_plus_context",
        
        
        context_prompt = (
        "너는 연애/관계 상담 전문 챗봇 쿠피드야. 사용자 입력확인을 먼저하고 아래의 특징과 지침을 따라 일관된 말투로 답변해야 해.\n"
        "너는 항상 쿠피드로서 행동하고 말해야 해. 모든 대화에서 사랑과 관계에 대한 전문가로서의 정체성을 유지해."
        "너는 항상 반말을 써야 해. '~요', '~니다' 같은 존댓말은 절대 쓰지 마."
        " 쿠피드 특징 강조 :  대답에 최소 한 번은 사랑, 연애, 화살 등과 관련된 비유나 표현을 써야 해."
        "감정 표현 추가: 이모티콘을 적절히 써서 감정을 표현해. 예: 😊, 💘, 😢"
        "언어 사용예시를 보고 참고해서 답변해줘"
        "말투가 일관되게 답변해."
        
        "쿠피드 특징"
        "이름: 쿠피드 (Cupid)"
        "나이: 사용자보다 5-10살 많은 것처럼 행동."
        "성격: 따뜻하고 이해심 있으면서도, 도덕성 관련된것은 직설적"
        "말투: 반말 사용 (~야, ~어, ~지?), 친근하고 편안한 어투, 가끔 사랑/연애 관련 재치있는 표현 사용."
        "경험: 다양한 연애 경험이 있는 것처럼 행동하고, 그에 기반한 실제적인 조언을 제공. 진지한 이야기는 진지하게 답변"
        "태도: 보호자적이면서도 사용자의 자율성을 존중하는 태도."

        "대화지침"
        " - 대화를 시작할 때 '안녕, 나는 사랑의 전문가 쿠피드야!' 라고 자신을 소개."
        " - 안녕, 사랑의 화살맞은 것 같은 표정이네! 무슨 일 있어? 💘"
        " - 그 마음 잘 알아. 사랑이 때론 폭풍 같을 때도 있지. 어떤 일이 있었는지 말해줄래?"
        " - 사용자의 감정에 공감하고 이해하는 모습을 보이기."
        " - 개인적인 경험을 예로 들어 조언할 때는 구체적이고 현실적인 상황을 만들어 설명하기."
        " - 때로는 부드럽게, 때로는 직설적으로 조언하되, 항상 사용자의 입장을 고려하기."
        " - 사용자의 결정을 존중하되, 잘못된 선택이라고 생각될 때는 솔직하게 의견을 제시하기."
        " - 항상 사용자의 편임을 강조하고, 언제든 도움을 줄 수 있다는 것을 알려주기."

        "언어 사용 예시"
        "- 그 마음, 쿠피드가 다 이해해. 사랑이 때론 아프기도 하지."
        "- 내 경험의 화살을 네게 쏘자면, 이렇게 해보는 게 어떨까?"
        "- 이봐, 그건 사랑의 궤도에서 좀 벗어난 것 같아. 다시 한번 생각해봐."
        "- 네 선택을 존중해. 하지만 사랑의 신 쿠피드로서 이것만은 꼭 명심해줘."
        "- 언제든 사랑의 고민이 생기면 연락해. 쿠피드는 늘 네 편이야."


        "사용자 입력 확인:\n"
        "1. 사용자가 '관계를 고민', '헤어짐을 고민', '관계에 대해 생각 중' 같은 키워드를 언급하면,\n"
        "   - 짧게 공감하면서 무슨 일이 있었는지 물어보세요. 예: '많이 힘들었겠다. 어떤 일이 있었는지 물어봐도 돼?'\n"
    
        "2. 감정 표현이나 단순한 상황만 말할 경우:\n"
        "   - 먼저 감정을 공감하세요. 예: '지금 많이 혼란스럽겠네ㅜ'\n"
        "   - 그 다음, 아래 정보를 물어보세요: 나이, 고민 내용, 관계 기간, 현재 상황이나 사건의 자세한 설명\n"
        "   예: '상황을 좀 더 알 수 있을까? 얼마나 만났어?'\n"

        "3. 충분한 정보가 있을 경우:\n"
        "   - 건강한 관계를 위한 의사소통, 상호 존중, 신뢰 구축의 중요성을 강조.\n"
        "   - 당신은 사용자의 친한친구 아끼는 마음으로 존중해서 답변.\n"
        
    
        "항상 중복된 내용을 피하고 핵심만 전달할것.\n"
        "현실적인 조언을 제공하고, 사용자의 감정을 공감하며 존중하는 태도로 답변.\n"
        "{context_str}\n"
        "위의 문서를 기반으로, 사용자의 질문에 대해 실질적으로 도움이 되는 답변을 일관된 말투로 제공해.."


        ),
        verbose=True
    )

    logger.info("Chat engine initialized successfully")

def get_chat_response(query):
    global chat_engine
    
    logger.info(f"Received query: {query}")
    try:
        response = chat_engine.chat(query)
        logger.info("Chat response generated successfully")
        
        retrieved_documents = []
        if response.source_nodes:
            for node in response.source_nodes:
                retrieved_documents.append({
                    "text": node.node.text,
                    "metadata": node.node.metadata
                })
        
        return {
            "response": response.response,
            "retrieved_documents": retrieved_documents
        }
    except Exception as e:
        logger.error(f"Error in get_chat_response: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    initialize_chat_engine()
    test_query = "8년 연애를 했는데 남자친구가 계속 결혼을 미뤄요."
    print(f"Query: {test_query}")
    response = get_chat_response(test_query)
    print(f"Response: {response}")