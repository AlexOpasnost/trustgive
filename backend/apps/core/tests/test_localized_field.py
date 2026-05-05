"""Tests for LocalizedTextField (per ADR-006)."""
from __future__ import annotations

import pytest

from apps.core.fields import LocalizedTextField, _empty_localized
from apps.core.serializers import LocalizedSerializerField


def test_empty_localized_is_en_ru_pair():
    value = _empty_localized()
    assert value == {"en": "", "ru": ""}


def test_field_default_is_dict():
    field = LocalizedTextField()
    default = field.get_default()
    assert default == {"en": "", "ru": ""}


def test_field_get_prep_value_fills_missing_keys():
    field = LocalizedTextField()
    out = field.get_prep_value({"en": "Hello"})
    assert out == {"en": "Hello", "ru": ""}


def test_field_handles_none_input():
    field = LocalizedTextField()
    assert field.get_prep_value(None) == {"en": "", "ru": ""}


def test_serializer_emits_both_keys_even_when_one_missing():
    s = LocalizedSerializerField()
    assert s.to_representation({"en": "Hi"}) == {"en": "Hi", "ru": ""}
    assert s.to_representation({}) == {"en": "", "ru": ""}
    assert s.to_representation(None) == {"en": "", "ru": ""}


def test_serializer_to_internal_value_coerces_strings():
    s = LocalizedSerializerField()
    out = s.to_internal_value({"en": 42, "ru": "Привет"})
    assert out == {"en": "42", "ru": "Привет"}


def test_serializer_rejects_non_dict():
    s = LocalizedSerializerField()
    with pytest.raises(Exception):
        s.to_internal_value("not a dict")
