from enum import Enum


class FilterOp(str, Enum):
    contains: str = "contains"
    exists: str = "exists"
    lt: str = "lt"
    le: str = "le"
    eq: str = "eq"
    ne: str = "ne"
    ge: str = "ge"
    gt: str = "gt"
