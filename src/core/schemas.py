from pydantic import BaseModel as Base, ConfigDict


class BaseModel(Base):
    model_config = ConfigDict(strict=True, from_attributes=True)
