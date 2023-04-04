from typing import Optional
from pydantic import BaseModel


class Regularizations(BaseModel):
    id: Optional[int]
    user_id: int
    year: int
    status: int
    regimes: str
    pending: Optional[list]
    paid: Optional[list]
    periodicity: Optional[str]
    additional_information: Optional[dict]
