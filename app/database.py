from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs, async_sessionmaker

class Base(AsyncAttrs, DeclarativeBase):
    pass

engine = create_async_engine(
    "sqlite+aiosqlite:///./sql_app.db", connect_args={"check_same_thread": False}, 
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)