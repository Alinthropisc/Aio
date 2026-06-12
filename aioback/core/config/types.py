from typing import Annotated

from pydantic import SecretStr, UrlConstraints
from pydantic.networks import AnyUrl

DatabaseDSN = Annotated[
    AnyUrl,
    UrlConstraints(allowed_schemes=["postgresql+psycopg", "mysql+aiomysql"]),
]

RedisDSN = Annotated[
    AnyUrl,
    UrlConstraints(allowed_schemes=["redis", "rediss"]),
]

SecretValue = SecretStr
