from os import getenv


from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    url: str = str(getenv("POSTGRES_URL"))
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig())
