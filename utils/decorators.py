from functools import wraps

import logging

logger = logging.getLogger(__name__)


def commit_session(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self._session_factory() as session:
            try:
                result = await func(self, session, *args, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка транзакции в {func.__name__}: {e}")
                raise

    return wrapper


def read_only_session(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self._session_factory() as session:
            return await func(self, session, *args, **kwargs)

    return wrapper
