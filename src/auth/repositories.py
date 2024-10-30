from src.auth.models import BlacklistToken, User
from src.core.repository import SQLAlchemyRepository


class AuthRepository(SQLAlchemyRepository[User]):
    pass


class BlacklistTokenRepository(SQLAlchemyRepository[BlacklistToken]):
    pass
