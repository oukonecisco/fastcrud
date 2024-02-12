from datetime import datetime
from typing import Annotated

from fastapi import Query


class CommonQueryParams:
    def __init__(
        self,
        created: Annotated[datetime | None, Query()] = None,
        created__gt: Annotated[datetime | None, Query()] = None,
        created__gte: Annotated[datetime | None, Query()] = None,
        created__lt: Annotated[datetime | None, Query()] = None,
        created__lte: Annotated[datetime | None, Query()] = None,
        updated: Annotated[datetime | None, Query()] = None,
        updated__gt: Annotated[datetime | None, Query()] = None,
        updated__gte: Annotated[datetime | None, Query()] = None,
        updated__lt: Annotated[datetime | None, Query()] = None,
        updated__lte: Annotated[datetime | None, Query()] = None,
    ):
        self.created = created
        self.created__gt = created__gt
        self.created__gte = created__gte
        self.created__lt = created__lt
        self.created__lte = created__lte
        self.updated = updated
        self.updated__gt = updated__gt
        self.updated__gte = updated__gte
        self.updated__lt = updated__lt
        self.updated__lte = updated__lte


async def get_common_parameters(
    limit: Annotated[int, Query(min=1, max=100)] = 10,
    offset: Annotated[int, Query(min=0)] = 0,
    ordering: Annotated[str | None, Query()] = None,
) -> dict:
    """Get common api parameters."""
    return {
        "limit": limit,
        "offset": offset,
        "ordering": ordering,
    }


async def get_common_match_parameters(
    created: Annotated[datetime | None, Query()] = None,
    created__gt: Annotated[datetime | None, Query()] = None,
    created__gte: Annotated[datetime | None, Query()] = None,
    created__lt: Annotated[datetime | None, Query()] = None,
    created__lte: Annotated[datetime | None, Query()] = None,
    updated: Annotated[datetime | None, Query()] = None,
    updated__gt: Annotated[datetime | None, Query()] = None,
    updated__gte: Annotated[datetime | None, Query()] = None,
    updated__lt: Annotated[datetime | None, Query()] = None,
    updated__lte: Annotated[datetime | None, Query()] = None,
) -> dict:
    """Get common match query parameters."""
    return {
        "created": created,
        "created__gt": created__gt,
        "created__gte": created__gte,
        "created__lt": created__lt,
        "created__lte": created__lte,
        "updated": updated,
        "updated__gt": updated__gt,
        "updated__gte": updated__gte,
        "updated__lt": updated__lt,
        "updated__lte": updated__lte,
    }
