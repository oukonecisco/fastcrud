import gc
import uuid
import json
import rocksdb
import pydantic
import operator
import functools
from fastcrud import path
from fastcrud.storage import BaseStorage
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder


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


class UpdateData(rocksdb.interfaces.AssociativeMergeOperator):
    def merge(self, key, existing_value, value):
        if existing_value:
            existing_value = json.loads(existing_value)
            value = json.loads(value)
            for attr, val in value.items():
                if isinstance(value[attr], list):
                    existing_value[attr] = list(
                        set(existing_value[attr] + val)
                    )
                else:
                    existing_value[attr] = val
            return (True, json.dumps(existing_value).encode("utf-8"))
        return (True, value)

    def name(self):
        return b"UpdateData"


TABLE_FACTORY = rocksdb.BlockBasedTableFactory(
    filter_policy=rocksdb.BloomFilterPolicy(10),
    block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
    block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)),
)


class LocalStorage(BaseStorage):

    default_settings = {
        "create_if_missing": True,
        "max_open_files": 300000,
        "write_buffer_size": 67108864,
        "max_write_buffer_number": 3,
        "target_file_size_base": 67108864,
        "merge_operator": UpdateData(),
        "table_factory": TABLE_FACTORY,
    }

    def __init__(self, model=None, **settings):
        self._db = None
        self.dbname = f"{model.__name__}".lower()
        self.model = model
        self.default_settings.update(**settings)
        self.opts = rocksdb.Options(**self.default_settings)

    @property
    def dbpath(self):
        return f"{path.root()}/rocksdbs"

    @property
    def db(self):
        if not hasattr(self, "_db"):
            raise Exception("DB not initialized.")
        assert self._db, "DB not initialized."
        return self._db

    def validator(
        self, obj: BaseCrudModel, model: BaseCrudModel = None
    ):
        return isinstance(obj, model)

    def serialize(
        self, obj: BaseCrudModel, model: BaseCrudModel = None
    ):
        if not self.validator(obj, model=model):
            raise Exception(f"{obj} is not serializable.")
        return obj.json().encode("utf-8")

    def deserialize(
        self, obj: bytes, model: BaseCrudModel = None
    ) -> pydantic.BaseModel:
        return model(**json.loads(obj))

    def get(self, uid: str):
        obj = self.db.get(uid.encode("utf-8"))
        if obj is None:
            raise HTTPException(status_code=404)
        return {"id": uid, "item": self.deserialize(obj, model=self.model)}

    def create(self, obj):
        uid = str(obj.uid) or str(uuid.uuid1())
        self.db.put(uid.encode("utf-8"), self.serialize(obj, model=self.model))
        return {"id": uid, "item": obj}

    def put(self, uid, obj):
        obj.uid = uid
        self.db.put(uid.encode("utf-8"), self.serialize(obj, model=self.model))
        return {"id": uid, "item": obj}

    def patch(self, uid, obj):
        self.db.merge(
            uid.encode("utf-8"),
            json.dumps(
                jsonable_encoder(
                    obj.dict(exclude_unset=True)
                )
            ).encode("utf-8"),
        )
        return {"id": uid, "item": obj.dict(exclude_unset=True)}

    def delete(self, uid):
        try:
            self.db.delete(uid.encode("utf-8"))
        except Exception:
            raise HTTPException(status_code=404)
        return {"id": uid, "deleted": True}

    def get_many(self, field, value, opr):
        return list(self.find(field, value, opr))

    def put_many(self, *objs):
        ...

    def patch_many(self, *objs):
        ...

    def delete_many(self, *uids):
        ...

    def find(
        self, field, value, opr="eq", key=default_filter,
    ):
        iterdb = self.db.itervalues()
        iterdb.seek_to_first()
        deserializer = functools.partial(self.deserialize, model=self.model)
        return map(
            lambda obj: {"id": obj.uid, "item": obj},
            filter(
                functools.partial(key, field, value, opr=opr),
                map(deserializer, iterdb),
            ),
        )

    def start(self):
        if self._db:
            self.close()

        path.pathlib.Path(self.dbpath).mkdir(exist_ok=True)
        self._db = rocksdb.DB(f"{self.dbpath}/{self.dbname}.db", self.opts)

    def stop(self):
        """
        https://github.com/twmht/python-rocksdb/issues/10
        """
        del self._db
        gc.collect()
