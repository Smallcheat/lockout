"""Typed data model for management-plane models.

Edge direction: ``source`` depends on ``target`` ("source requires target").
Cross-references (edge endpoints, capability requirements, ...) are plain node ids here;
checking that they resolve is the job of the loader's semantic lint.
"""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ID_PATTERN = r"^[a-z0-9][a-z0-9_.-]*$"
TAG_PATTERN = r"^[a-z0-9][a-z0-9_.-]*(:[a-z0-9][a-z0-9_.-]*)?$"

Id = Annotated[str, StringConstraints(pattern=ID_PATTERN)]
Tag = Annotated[str, StringConstraints(pattern=TAG_PATTERN)]


class EdgeType(StrEnum):
    """The four dependency types. ADR-0001 keeps this set closed."""

    START = "requires_to_start"
    AUTHENTICATE = "requires_to_authenticate"
    REACH = "requires_to_reach"
    AUTHORIZE = "requires_to_authorize"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Node(_Strict):
    id: Id
    kind: Annotated[str, StringConstraints(min_length=1)]
    description: str | None = None
    tags: list[Tag] = Field(default_factory=list)


class Edge(_Strict):
    source: Id = Field(alias="from")
    target: Id = Field(alias="to")
    type: EdgeType


class Capability(_Strict):
    id: Id
    description: str | None = None
    requires: list[Id] = Field(default_factory=list)


class BreakGlassPath(_Strict):
    id: Id
    capability: Id
    description: str | None = None
    requires: list[Id] = Field(default_factory=list)


class RedundancyGroup(_Strict):
    """Members that can stand in for each other; at least ``min_available`` must stay up."""

    id: Id
    members: list[Id] = Field(min_length=2)
    min_available: int = Field(default=1, ge=1)


class Model(_Strict):
    name: Annotated[str, StringConstraints(min_length=1)]
    description: str | None = None
    nodes: list[Node] = Field(min_length=1)
    edges: list[Edge] = Field(default_factory=list)
    capabilities: list[Capability] = Field(default_factory=list)
    break_glass_paths: list[BreakGlassPath] = Field(default_factory=list)
    redundancy_groups: list[RedundancyGroup] = Field(default_factory=list)
