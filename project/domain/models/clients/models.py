import datetime
import enum

import pydantic


class ColombianDocumentType(enum.Enum):
    CEDULA = enum.auto()
    CEDULA_EXTRANJERIA = enum.auto()
    PPT = enum.auto()
    PASAPORTE = enum.auto()


class IdentityDocument(pydantic.BaseModel):
    name: str
    document_type: ColombianDocumentType
    document_number: str


class Client(pydantic.BaseModel):
    id_client: str
    identity_document: IdentityDocument
    creation_date: datetime.date
