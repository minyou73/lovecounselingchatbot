from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from lovechatengine import chat_engine  # 기존 lovechatengine.py에서 가져옴

app = FastAPI()

# CORS 설정: React 프론트엔드와 FastAPI 백엔드 간 통신 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청 데이터 모델 정의
class QueryRequest(BaseModel):
    query: str

# 챗봇 엔드포인트
@app.post("/chat")
async def chat(request: QueryRequest):
    query = request.query
    # ChatEngine을 통해 질문에 대한 답변 생성
    response = chat_engine.chat(query)
    return {"response": response}

# FastAPI 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
