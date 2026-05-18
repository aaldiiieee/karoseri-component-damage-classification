import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL,
    future=True,
    echo=False,
    pool_size=int(os.getenv('POOL_SIZE', 10)),
    max_overflow=int(os.getenv('MAX_OVERFLOW', 20)),
    pool_timeout=int(os.getenv('POOL_TIMEOUT', 30)),
    pool_recycle=int(os.getenv('POOL_RECYCLE', 1800)),
    pool_pre_ping=os.getenv('POOL_PRE_PING', 'true').lower() != 'false',
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session