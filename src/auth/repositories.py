from src.auth.models import AuthCode, BlacklistToken, User
from src.core.repository import SQLAlchemyRepository


class AuthRepository(SQLAlchemyRepository[User]):
    pass


class BlacklistTokenRepository(SQLAlchemyRepository[BlacklistToken]):
    pass

class AuthCodeRepository(SQLAlchemyRepository[AuthCode]):
    pass