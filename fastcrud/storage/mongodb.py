import operator

import daiquiri
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from fastcrud.storage.aggregation import (
    process_facet_stage,
    process_ordering_stage,
    process_query_parameter_stage,
)
from fastcrud.storage.commun import BaseStorage
from fastcrud.utils import create_in_db_model

LOGGER = daiquiri.getLogger(__name__)


def default_filter(field, value, obj, opr="eq"):
    """
    Containment Test	obj in seq	contains(seq, obj)
    Truth Test	obj	truth(obj)
    Ordering	a < b	lt(a, b)
    Ordering	a <= b	le(a, b)
    Equality	a == b	eq(a, b)
    Difference	a != b	ne(a, b)
    Ordering	a >= b	ge(a, b)
    Ordering	a > b	gt(a, b)
    """
    OPERATORS = {
        "contains",
        "exists",
        "lt",
        "le",
        "eq",
        "ne",
        "ge",
        "gt",
    }
    assert opr in OPERATORS, "find operation: invalid operator"
    if opr == "contains":
        field = vars(obj).get(field)
        if not isinstance(field, (str, list, tuple, set, frozenset)):
            field = list()
        return operator.contains(field, value)
    if opr == "exists":
        return operator.truth(vars(obj).get(field))
    return vars(operator)[opr](vars(obj).get(field), value)


class MongoStorage(BaseStorage):
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        model,
        collection: str | None = None,
    ):
        self.db = db
        self.collection = collection or f"{model.__name__}"
        self.model = model
        self.db_model = create_in_db_model(model)

    async def get(self, uid: str):
        item = await self.db[self.collection].find_one({"_id": uid})
        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"{uid=} was not found in {self.collection}",
            )
        return self.db_model(**item)

    async def create(self, items):
        items_in_db = []
        for item in items:
            items_in_db.append(
                self.db_model(
                    **{
                        **item.model_dump(),
                        "created": item.updated,
                    }
                )
            )
        try:
            results = await self.db[self.collection].insert_many(
                jsonable_encoder(items_in_db)
            )
            docs = (
                await self.db[self.collection]
                .find({"_id": {"$in": results.inserted_ids}})
                .to_list(None)
            )
            return jsonable_encoder(
                list(map(lambda doc: self.db_model(**doc), docs))
            )
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))

    def update(self, items):
        ...

    def replace(self, items):
        ...

    def delete(self, uids):
        ...

    async def find(
        self, common, common_match, filters, facets, *args, **kwargs
    ):
        stages: list[dict] = []

        limit = common.get("limit", 10)
        offset = common.get("offset", 0)
        ordering = common.get("ordering")

        pre_match_stages: list[dict] = []
        process_query_parameter_stage(pre_match_stages, common_match | filters)

        if pre_match_stages:
            stages.append({"$match": {"$and": pre_match_stages}})

        # Ordering stage
        process_ordering_stage(stages, ordering)

        # Facets stage
        process_facet_stage(
            stages,
            [],
            facets,
            limit,
            offset,
        )

        return stages
