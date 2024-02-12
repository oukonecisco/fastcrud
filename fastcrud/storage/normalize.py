# -*- coding: utf-8 -*-
__author__ = "CX Catalog Team"
__email__ = "cxcatalog-notifications@cisco.com"
__copyright__ = """
Copyright 2022, Cisco Systems, Inc.
All Rights Reserved.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""  # noqa


from datetime import datetime
from typing import Any, Sequence

import daiquiri

from cxc_item.settings import SETTINGS
from cxc_item.utils.date import datetime_to_iso8601_with_z_suffix

LOGGER = daiquiri.getLogger(__name__)
FILTER_CONTAINS_OPERATORS = ["contains", "icontains"]
FILTER_LIST_OPERATORS = ["in", "nin"]
FILTER_RANGE_OPERATORS = ["gt", "gte", "lt", "lte"]
MONGODB_LIST_OPERATORS = ["$in", "$nin"]


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


def normalize_collection_from_rabbitmq(collection: str) -> str:
    """Normalize collection from rabbitmq."""
    return collection.replace("__", ".")


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


def normalize_collection_name_to_api(
    field_name: str, collection_name: str
) -> str:
    """Normalize collection name to API."""

    normalized_collection_name = (
        collection_name[:-1]
        if collection_name.endswith("s")
        else collection_name
    )

    normalized_field_name = SETTINGS.metadata_api_names.get(
        field_name, field_name[:-1] if field_name.endswith("s") else field_name
    )

    if field_name not in SETTINGS.metadata_common_fields:
        return f"{normalized_collection_name}/{normalized_field_name}"
    return normalized_field_name
