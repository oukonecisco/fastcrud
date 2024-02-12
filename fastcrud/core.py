import uuid
from datetime import datetime
from typing import Annotated, Any

import pydantic
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient

from fastcrud.dependencies import (
    get_common_match_parameters,
    get_common_parameters,
)
from fastcrud.storage.commun import BaseStorage
from fastcrud.storage.mongodb import MongoStorage
from fastcrud.utils import (
    create_in_db_model,
    create_update_model,
    run_async_or_sync,
)


class BaseCrudModel(pydantic.BaseModel):
    created: datetime | None = None
    updated: datetime = pydantic.Field(default_factory=datetime.now)


class BaseCrud:
    def __init__(
        self,
        model: BaseCrudModel,
        storage: MongoStorage,
        filters: Any,
    ):
        self.model = model
        self.storage = storage
        self.filters = filters
        self.db_model = create_in_db_model(model)
        self.update_model = create_update_model(model)

        async def create(items: list[model]) -> list[self.db_model]:
            """
            Create an object, generating a unique id by default
            """
            return await run_async_or_sync(self._create, items)

        async def update(
            items: list[self.update_model],
        ) -> list[self.db_model]:
            """
            Create an object, generating a unique id by default
            """
            return await run_async_or_sync(self._update, items)

        async def replace(
            items: list[self.db_model],
        ) -> list[self.db_model]:
            """
            Create an object, generating a unique id by default
            """
            return await run_async_or_sync(self._replace, items)

        async def get(uid: str) -> self.db_model:
            """
            Get an object by its unique id
            """
            return await run_async_or_sync(self._get, uid)

        async def find(
            common: Annotated[dict, Depends(get_common_parameters)],
            common_match: Annotated[
                dict, Depends(get_common_match_parameters)
            ],
            filters: Annotated[filters, Depends(filters)],
            facets: Annotated[list[str], Query(default_factory=list)],
        ):
            """
            Get one or more objects by a comparison operator

            See: :func:`fastcrud.storage.local.default_filter` docstring
            for more details
            """
            return await run_async_or_sync(
                self._find, common, common_match, filters, facets
            )

        async def delete(uids: Annotated[list[str], Query()]):
            """
            Delete an object by unique id
            """
            return await run_async_or_sync(self._delete, uids)

        self.get = get
        self.create = create
        self.update = update
        self.replace = replace
        self.delete = delete
        self.find = find

    async def _get(self, uid):
        return await run_async_or_sync(self.storage.get, uid)

    async def _find(
        self, common, common_match, filters, facets, *args, **kwargs
    ):
        return await run_async_or_sync(
            self.storage.find,
            common,
            common_match,
            filters,
            facets,
            *args,
            **kwargs,
        )

    async def _create(self, items):
        return await run_async_or_sync(self.storage.create, items)

    async def _update(self, items):
        return await run_async_or_sync(self.storage.update, items)

    async def _replace(self, items):
        return await run_async_or_sync(self.storage.replace, items)

    async def _delete(self, uids: list[str]):
        return await run_async_or_sync(self.storage.delete, uids)


class CRUDRouter(APIRouter):
    def __init__(
        self,
        *args,
        collection: str | None = None,
        model: BaseCrudModel | None = None,
        crud_cls: BaseCrud | None = None,
        storage_cls: BaseStorage | None = None,
        storage_settings: dict | None = None,
        filters=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.model = model or BaseCrudModel
        self.crud_cls = crud_cls or BaseCrud
        self.storage_cls = storage_cls or MongoStorage
        self.collection = collection or self.model.__name__
        self.storage_settings: dict = storage_settings or {}

        mongodb_client = AsyncIOMotorClient(
            self.storage_settings["mongodb_url"]
        )

        self.storage: MongoStorage = self.storage_cls(
            mongodb_client[self.storage_settings["mongodb_name"]],
            self.model,
            self.collection,
        )

        self.crud = self.crud_cls(
            self.model,
            self.storage,
            filters=filters or (lambda: None),
        )
        self.crud.get = self.get("/{uid}")(self.crud.get)
        self.crud.find = self.get("/")(self.crud.find)
        self.crud.create = self.post("/")(self.crud.create)
        self.crud.update = self.patch("/")(self.crud.update)
        self.crud.replace = self.patch("/")(self.crud.replace)
        self.crud.delete = self.delete("/")(self.crud.delete)
