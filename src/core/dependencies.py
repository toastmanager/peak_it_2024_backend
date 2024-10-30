from src.core.database import async_session_maker


async def get_async_session():
    async with async_session_maker() as db:
        yield db
