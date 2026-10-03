"""Scenario schema: a failure set chosen by node name, by tag selector, or both."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from lockout.schema.model import Id, Tag


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TagSelector(_Strict):
    """Selects every node that carries all of ``tags_all``."""

    tags_all: list[Tag] = Field(min_length=1)


class FailureSpec(_Strict):
    nodes: list[Id] = Field(default_factory=list)
    select: TagSelector | None = None


class Scenario(_Strict):
    name: Annotated[str, StringConstraints(min_length=1)]
    description: str | None = None
    failed: FailureSpec
