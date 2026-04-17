"""Shared helpers for forwarding optional SDK list parameters."""

from __future__ import annotations


def build_list_kwargs(
    *,
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> dict[str, str | int]:
    """Return only the list parameters explicitly provided by the caller."""
    kwargs: dict[str, str | int] = {}

    if filter is not None:
        kwargs["filter"] = filter
    if after is not None:
        kwargs["after"] = after
    if first is not None:
        kwargs["first"] = first
    if sort is not None:
        kwargs["sort"] = sort

    return kwargs
