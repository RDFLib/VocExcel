from pydantic import BaseModel, ValidationError, validator
from pydantic import AnyHttpUrl
import datetime

ORGANISATIONS = [
    "CGI",
    "GA",
    "GGIC",
    "GSQ",
    "ICSM",
]


class Vocabulary(BaseModel):
    uri: AnyHttpUrl
    title: str
    description: str
    created: datetime.date
    modified: datetime.date
    creator: str
    publisher: str
    version: str
    provenance: str
    custodian: str
    ecat_doi: AnyHttpUrl

    @validator("creator")
    def creator_must_be_from_list(cls, v):
        if v not in ORGANISATIONS:
            raise ValueError(f"Organisations must selected from the Organisations list: {', '.join(ORGANISATIONS)}")
        return v

    @validator("publisher")
    def publisher_must_be_from_list(cls, v):
        if v not in ORGANISATIONS:
            raise ValueError(f"Organisations must selected from the Organisations list: {', '.join(ORGANISATIONS)}")
        return v


class Concept(BaseModel):
    uri: AnyHttpUrl
    pref_label: str
    alt_labels: str
    definition: str
    provenance: str
    children: list[AnyHttpUrl]
    other_ids: list[str]
    home_vocab_uri: AnyHttpUrl
    provenance: str


class Collection(BaseModel):
    uri: AnyHttpUrl
    pref_label: str
    definition: str
    members: list[AnyHttpUrl]
    provenance: str
