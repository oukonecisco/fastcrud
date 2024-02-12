import daiquiri
from fastapi import Depends

from demo.dependencies import item_query_params
from demo.schemas import ItemModel
from demo.settings import SETTINGS
from fastcrud.core import BaseCrud, CRUDRouter

LOGGER = daiquiri.getLogger(__name__)


router = CRUDRouter(
    collection="items",
    model=ItemModel,
    prefix="/item",
    tags=["item"],
    storage_settings={
        "mongodb_url": SETTINGS.mongodb_url,
        "mongodb_name": SETTINGS.mongodb_name,
    },
    crud_cls=BaseCrud,
    filters=item_query_params,
)


@router.get("/@me")
def me():
    return {}
