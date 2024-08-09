import datetime
import enum

import pydantic

from project.commons import random_keys


class ProductTypes(enum.Enum):
    LOAN = enum.auto()


class Product(pydantic.BaseModel):
    product_id: str = random_keys.generate_unique_id()
    creation_utc_datetime: datetime.datetime = datetime.datetime.utcnow()
    product_type: ProductTypes
