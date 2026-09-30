from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[1] / "examples" / "authorization-filter.py"
SPEC = importlib.util.spec_from_file_location("authorization_filter", MODULE_PATH)
assert SPEC and SPEC.loader
authorization_filter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(authorization_filter)

build_group_filter = authorization_filter.build_group_filter

FINANCE = "11111111-1111-1111-1111-111111111111"
ENGINEERING = "22222222-2222-2222-2222-222222222222"


def test_single_group_filter():
    result = build_group_filter([FINANCE])
    assert result == (
        "group_ids/any(g:search.in(g, "
        "'11111111-1111-1111-1111-111111111111', ','))"
    )


def test_multiple_groups_are_supported():
    result = build_group_filter([FINANCE, ENGINEERING])
    assert FINANCE in result
    assert ENGINEERING in result


def test_duplicate_groups_are_removed():
    result = build_group_filter([FINANCE, FINANCE])
    assert result.count(FINANCE) == 1


def test_empty_group_set_fails_closed():
    assert build_group_filter([]) == "group_ids/any(g: false)"


def test_blank_values_are_ignored_then_fail_closed():
    assert build_group_filter([" ", ""]) == "group_ids/any(g: false)"


@pytest.mark.parametrize(
    "malicious_value",
    [
        "not-a-guid",
        "11111111-1111-1111-1111-111111111111') or true or ('",
        "*",
        "finance-admins",
    ],
)
def test_malformed_or_injected_group_ids_are_rejected(malicious_value):
    with pytest.raises(ValueError):
        build_group_filter([malicious_value])
