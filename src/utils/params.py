from dataclasses import dataclass, field
from typing import Annotated

from fastapi import Query


@dataclass
class CommonQueryParams:
    page_number: Annotated[int, Query(gt=0)] = 1
    page_size: Annotated[int, Query(gt=0)] = 10
    sort: Annotated[list[str], Query(default_factory=list)] = field(default_factory=list)
