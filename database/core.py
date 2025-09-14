from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.models import Base



class Database:
    def __init__(self, database_url: str):
        # Создаем асинхронный движок
        self.engine = create_async_engine(
            database_url,
            echo=False,  # Показывать SQL запросы в логах
            future=True  # Включаем режим будущего (обязательно для 2.0)
        )

        # Создаем асинхронную сессию
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self):
        """Создание таблиц в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self):
        """Получение сессии с автоматическим управлением"""
        session = self.async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()