from typing import Annotated

from fastapi import Query

from fastcrud.dependencies import CommonQueryParams


class ItemQueryParams(CommonQueryParams):
    def __init__(
        self,
        name: Annotated[list[str] | None, Query()] = None,
        name__contains: Annotated[str | None, Query()] = None,
        name__icontains: Annotated[str | None, Query()] = None,
    ):
        self.name = name
        self.name__contains = name__contains
        self.name__icontains = name__icontains


def item_query_params(
    name: Annotated[list[str] | None, Query()] = None,
    des: Annotated[list[str] | None, Query()] = None,
    name__contains: Annotated[str | None, Query()] = None,
    name__icontains: Annotated[str | None, Query()] = None,
):
    return {
        "name": name,
        "name__contains": name__contains,
        "name__icontains": name__icontains,
    }
