from llama_index.embeddings.openai import OpenAIEmbedding  # OpenAI 임베딩 사용
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

import os
os.environ["OPENAI_API_KEY"] = ''



# 문서 로드
documents = SimpleDirectoryReader("data").load_data()

# 글로벌 설정
Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-ada-002")
Settings.llm = OpenAI(model="gpt-3.5-turbo", request_timeout=360.0)

# VectorStoreIndex 생성
index = VectorStoreIndex.from_documents(
    documents,
    show_progress=True
)

# QueryEngine 생성 / 인덱스로 검색엔진으로 사용해라
query_engine = index.as_query_engine(streaming=True, similarity_top_k=1)

# 프롬프트 템플릿 설정
qa_prompt_tmpl_str = (
    "Context information is below. \n"
    "---------------------------\n"
    "{context_str}\n"
    "-------------------------------"
    "Given the context information above I want you to think step by step to answer the query in a crasp manner"
    "Query: {query_str}\n"
    "Answer: "
)
qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

# 쿼리 엔진에 프롬프트 템플릿 적용
query_engine.update_prompts(
    {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
)

# 쿼리 실행 및 결과 출력
response = query_engine.query("연락을 별로 안하는 남친, 제게 관심이 없는걸까요?  ")
print(response)
