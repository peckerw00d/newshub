from os import getenv


from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    url: str = str(getenv("POSTGRES_URL"))
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class RabbitMQConfig(BaseModel):
    url: str = str(getenv("RABBITMQ_URL"))


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig())
    rabbitmq: RabbitMQConfig = Field(default_factory=lambda: RabbitMQConfig())


def load_config() -> "Config":
    return Config()
