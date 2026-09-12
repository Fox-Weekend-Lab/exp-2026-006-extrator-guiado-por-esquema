import pytest

from schema_guided_extractor.schema import SchemaError, validate_schema


def test_accepts_scalars_and_simple_arrays():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "tags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["name"],
    }
    assert validate_schema(schema) is schema


@pytest.mark.parametrize(
    "schema",
    [
        {"type": "object", "properties": {"person": {"type": "object"}}},
        {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object"}}}},
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["other"]},
    ],
)
def test_rejects_unsupported_or_inconsistent_schemas(schema):
    with pytest.raises(SchemaError):
        validate_schema(schema)
