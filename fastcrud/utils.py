import asyncio
import typing
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

import daiquiri
import pydantic

LOGGER = daiquiri.getLogger(__name__)
FILTER_CONTAINS_OPERATORS = ["contains", "icontains"]
FILTER_LIST_OPERATORS = ["in", "nin"]
FILTER_RANGE_OPERATORS = ["gt", "gte", "lt", "lte"]
MONGODB_LIST_OPERATORS = ["$in", "$nin"]


async def run_async_or_sync(func: typing.Callable, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return func(*args, **kwargs)


def create_in_db_model(model):
    return pydantic.create_model(
        f"{model.__name__}InDb",
        id=(str, pydantic.Field(default_factory=uuid.uuid1, alias="_id")),
        __base__=model,
    )


def create_update_model(model, exclude: list[str] | None = None):
    return pydantic.create_model(
        f"{model.__name__}Update",
        __base__=create_in_db_model(model),
        **{
            field: (model.model_fields[field].annotation, None)
            for field in model.model_fields
            if field not in (exclude or ["_id", "created", "updated"])
        },
    )


def datetime_to_iso8601_with_z_suffix(value: datetime) -> str:
    """Convert datetime to ISO 8601 with Z suffix"""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    formatted_datetime: str = value.isoformat()
    if formatted_datetime.endswith("+00:00"):
        formatted_datetime = formatted_datetime[:-6] + "Z"
    return formatted_datetime


def build_parameter(parameter: str, operator: str | None, value: Any) -> dict:
    """Build parameter dictionary."""
    match_stages_dict: dict = {}
    if operator:
        if operator in FILTER_CONTAINS_OPERATORS:
            match_stages_dict[parameter] = {}
            match_stages_dict[parameter]["$regex"] = f".*{value}.*"
            if operator == "icontains":
                match_stages_dict[parameter]["$options"] = "i"
        else:
            match_stages_dict[parameter] = {}
            match_stages_dict[parameter][operator] = normalize_value(
                value, operator
            )
    else:
        match_stages_dict = {parameter: normalize_value(value, operator)}
    return match_stages_dict


def normalize_parameter(parameter: str) -> tuple[str, str | None]:
    """Normalize parameter."""
    LOGGER.debug("Normalizing parameter: '%s'", parameter)
    operator = None

    if "__" in parameter:
        parameters = parameter.split("__")
        if (
            parameters[-1] in FILTER_RANGE_OPERATORS
            or parameters[-1] in FILTER_LIST_OPERATORS
        ):
            parameter = ".".join(parameters[:-1])
            operator = f"${parameters[-1]}"
        elif parameters[-1] in FILTER_CONTAINS_OPERATORS:
            parameter = ".".join(parameters[:-1])
            operator = f"{parameters[-1]}"
        else:
            parameter = parameter.replace("__", ".")

    LOGGER.debug(
        "Normalized parameter: '%s', operator: '%s'", parameter, operator
    )
    return parameter, operator


def normalize_value(
    value: str | bool | datetime, operator: str | None
) -> str | bool | Sequence[str | bool | datetime]:
    """Normalize value."""
    if isinstance(value, datetime):
        return datetime_to_iso8601_with_z_suffix(value)
    elif operator in MONGODB_LIST_OPERATORS:
        return normalize_mongodb_list_operators(value, operator)

    return value


def normalize_mongodb_list_operators(
    value: str | bool | datetime, operator
) -> Sequence[str | bool | datetime]:
    """Normalize mongodb list operator value."""
    if isinstance(value, str):
        if "," in value:
            return value.split(",")
    return [value]
