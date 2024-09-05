from dataclasses import dataclass


@dataclass
class SourcePair:
    """Keeps track of a query and its source handler."""

    query: str
    handler_type: str
    operation: str = "default"  # TODO define operation types
