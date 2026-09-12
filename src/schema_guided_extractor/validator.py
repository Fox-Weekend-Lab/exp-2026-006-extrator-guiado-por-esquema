"""Validação determinística dos dados e evidências retornados pelo modelo."""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator


def validate_response(
    text: str, schema: dict[str, Any], response: Any
) -> dict[str, Any]:
    """Produz um relatório auditável para uma resposta no contrato data/evidence."""
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    data: Any = {}
    evidence: Any = {}

    if not isinstance(response, dict):
        errors.append(_issue("invalid_envelope", "$", "A resposta do modelo deve ser um objeto JSON."))
    else:
        data = response.get("data")
        evidence = response.get("evidence")
        if not isinstance(data, dict):
            errors.append(_issue("invalid_envelope", "$.data", "'data' deve ser um objeto."))
        if not isinstance(evidence, dict):
            errors.append(_issue("invalid_envelope", "$.evidence", "'evidence' deve ser um objeto."))

    if isinstance(data, dict):
        validator = Draft202012Validator(schema)
        schema_errors = sorted(
            validator.iter_errors(data), key=lambda error: (_path(error.absolute_path), error.message)
        )
        for error in schema_errors:
            errors.append(_issue("schema_validation", _path(error.absolute_path), error.message))

    properties = schema.get("properties", {})
    if isinstance(evidence, dict):
        for field, excerpts in evidence.items():
            field_path = f"$.evidence.{field}"
            if field not in properties:
                warnings.append(_issue("unknown_evidence_field", field_path, "A evidência refere-se a um campo desconhecido."))
            if not isinstance(excerpts, list) or any(not isinstance(item, str) for item in excerpts):
                errors.append(_issue("invalid_envelope", field_path, "Cada evidência deve ser uma lista de textos."))
                continue
            if not isinstance(data, dict) or field not in data or field not in properties:
                continue
            for index, excerpt in enumerate(excerpts):
                excerpt_path = f"{field_path}[{index}]"
                if not excerpt:
                    warnings.append(_issue("empty_evidence", excerpt_path, "O trecho de evidência está vazio."))
                elif excerpt not in text:
                    errors.append(
                        _issue(
                            "invalid_evidence",
                            excerpt_path,
                            "O trecho de evidência não foi localizado literalmente no texto-fonte.",
                        )
                    )

    return {
        "extracted_data": data,
        "evidence": evidence,
        "errors": errors,
        "warnings": warnings,
    }


def _path(parts: Any) -> str:
    path = "$"
    for part in parts:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


def _issue(category: str, path: str, message: str) -> dict[str, str]:
    return {"category": category, "path": path, "message": message}
