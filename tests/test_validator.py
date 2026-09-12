from schema_guided_extractor.validator import validate_response


SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "labels": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["name", "age"],
}


def test_valid_data_and_literal_evidence_have_no_errors():
    report = validate_response(
        "Ana tem 30 anos e gosta de livros.",
        SCHEMA,
        {"data": {"name": "Ana", "age": 30, "labels": ["livros"]}, "evidence": {"name": ["Ana"], "age": ["30"]}},
    )
    assert report["errors"] == []
    assert report["warnings"] == []


def test_schema_and_evidence_problems_are_reported():
    report = validate_response(
        "Ana tem 30 anos.",
        SCHEMA,
        {
            "data": {"name": 7, "labels": ["ok", 2]},
            "evidence": {"name": ["inexistente", ""], "unknown": ["Ana"]},
        },
    )
    categories = [item["category"] for item in report["errors"]]
    warnings = [item["category"] for item in report["warnings"]]
    assert categories.count("schema_validation") >= 3
    assert "invalid_evidence" in categories
    assert "empty_evidence" in warnings
    assert "unknown_evidence_field" in warnings
