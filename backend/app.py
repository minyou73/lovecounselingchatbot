from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # CORS 미들웨어 추가
from pydantic import BaseModel
import sys
import os
import logging

# 현재 디렉토리의 상위 디렉토리 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from lovechatengine import get_chat_response, initialize_chat_engine

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱의 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

# 서버 시작 시 챗봇 엔진 초기화
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing chat engine on startup...")
    try:
        initialize_chat_engine()
        logger.info("Chat engine initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing chat engine: {str(e)}", exc_info=True)

# POST 요청을 처리하는 엔드포인트
@app.post("/chat")
async def chat(query: Query):
    try:
        logger.info(f"Received query: {query.query}")
        result = get_chat_response(query.query)
        logger.info("Response generated successfully")
        return result
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
