# app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase  # 클래스 기반 Base 권장
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 1. 비동기 엔진 생성 (실무용 최적화 옵션 추가)
engine = create_async_engine(
    DATABASE_URL, 
    echo=True,           # SQL 로그 출력 (개발 단계에서 유용)
    pool_pre_ping=True,  # 연결 유효성 체크 (끊긴 연결 자동 복구)
    pool_recycle=3600    # 연결 유지 시간 설정
)

# 2. 비동기 세션 메이커
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. 최신 스타일의 Base 모델 정의
class Base(DeclarativeBase):
    pass

# 4. 의존성 주입 함수 (FastAPI 등에서 활용)
async def get_db():
    # 'async with'를 사용하면 에러 발생 시에도 자동으로 세션이 닫히므로 
    # 별도의 try/finally 없이도 안전하게 관리가 가능합니다.
    async with AsyncSessionLocal() as session:
        yield session