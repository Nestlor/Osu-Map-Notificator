from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL

class Base(DeclarativeBase):
    pass

engine = create_async_engine(DATABASE_URL)

SessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
