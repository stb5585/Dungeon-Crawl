"""Scoped guards for immediate combat reactions."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import ParamSpec, TypeVar

_Parameters = ParamSpec("_Parameters")
_Result = TypeVar("_Result")
_ReactionResult = TypeVar("_ReactionResult")
_ReactionKey = tuple[str, int]
_active_reactions: ContextVar[set[_ReactionKey] | None] = ContextVar(
    "active_reactions",
    default=None,
)


@contextmanager
def triggering_result() -> Iterator[None]:
    """Scope reaction execution to one root combat result."""
    active = _active_reactions.get()
    if active is not None:
        yield
        return
    token = _active_reactions.set(set())
    try:
        yield
    finally:
        _active_reactions.reset(token)


def reaction_result(
    resolver: Callable[_Parameters, _Result],
) -> Callable[_Parameters, _Result]:
    """Decorate a root combat resolver with a reaction execution scope."""

    @wraps(resolver)
    def wrapped(*args: _Parameters.args, **kwargs: _Parameters.kwargs) -> _Result:
        with triggering_result():
            return resolver(*args, **kwargs)

    return wrapped


def execute_reaction(
    reaction_id: str,
    owner: object,
    resolver: Callable[[], _ReactionResult],
) -> _ReactionResult | None:
    """Resolve one named reaction at most once for the current result."""
    active = _active_reactions.get()
    if active is None:
        return resolver()
    key = (reaction_id, id(owner))
    if key in active:
        return None
    active.add(key)
    return resolver()
