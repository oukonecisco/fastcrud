import json

import daiquiri

from fastcrud.utils import build_parameter, normalize_parameter

LOGGER = daiquiri.getLogger(__name__)


def process_lookup_items_stage(stages: list, item_fields: list[str]):
    """Process lookup items stage."""
    for field in item_fields:
        stages.append(
            {
                "$lookup": {
                    "from": field,
                    "localField": field,
                    "foreignField": "_id",
                    "as": field,
                }
            },
        )


def process_ordering_stage(stages: list, ordering: str | None):
    """Process ordering stage."""

    if ordering:
        ordering_dict = {}
        for ordering_field in ordering.split(","):
            if ordering_field[0] == "-":
                direction = -1
                field = ordering_field[1:]
            else:
                direction = 1
                field = ordering_field
            ordering_dict[field] = direction
        sort_stage = {"$sort": ordering_dict}
        LOGGER.debug(
            "Adding the following sort stage '%s'", json.dumps(sort_stage)
        )
        stages.append(sort_stage)


def process_facet_stage(
    stages: list,
    facet_list_fields: list[str],
    facet_other_fields: list[str],
    limit: int,
    offset: int,
):
    """Process facet stage."""

    facet_stage: dict[str, list] = {}
    for field in facet_list_fields + facet_other_fields:
        facet_stage[field] = []
        if field not in facet_other_fields:
            # Skip fields that are not of type list
            facet_stage[field].append({"$unwind": f"${field}"})

        facet_stage[field].append({"$sortByCount": f"${field}"})

    facet_stage["metadata"] = [{"$count": "count"}]
    facet_stage["results"] = [{"$skip": offset}, {"$limit": limit}]
    stages.append({"$facet": facet_stage})


def process_query_parameter_stage(match_stages: list, query_parameters: dict):
    """Process query parameter stage."""

    for parameter, value in query_parameters.items():
        if value is None:
            continue

        parameter, operator = normalize_parameter(parameter)

        if isinstance(value, list):
            for list_value in value:
                match_stages.append(
                    build_parameter(parameter, operator, list_value)
                )
        else:
            match_stages.append(build_parameter(parameter, operator, value))
