"""Validação do subconjunto de JSON Schema aceito pela aplicação."""

from __future__ import annotations

from typing import Any


SCALAR_TYPES = {"string", "number", "integer", "boolean"}
ROOT_KEYS = {"type", "properties", "required", "description"}
PROPERTY_KEYS = {"type", "items", "description"}


class SchemaError(ValueError):
    """Indica que o esquema usa recursos fora do subconjunto suportado."""


def validate_schema(schema: Any) -> dict[str, Any]:
    """Valida um esquema simplificado e o devolve quando ele é aceito."""
    if not isinstance(schema, dict):
        raise SchemaError("O esquema deve ser um objeto JSON.")

    _reject_unknown_keys(schema, ROOT_KEYS, "raiz do esquema")
    if schema.get("type") != "object":
        raise SchemaError("O esquema raiz deve declarar 'type' como 'object'.")

    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise SchemaError("O esquema raiz deve ter 'properties' como objeto.")

    required = schema.get("required", [])
    if not isinstance(required, list) or any(not isinstance(name, str) for name in required):
        raise SchemaError("'required' deve ser uma lista de nomes de propriedades.")
    if len(required) != len(set(required)):
        raise SchemaError("'required' não pode conter nomes repetidos.")
    missing = sorted(set(required) - set(properties))
    if missing:
        raise SchemaError(
            "Todo campo em 'required' deve existir em 'properties': " + ", ".join(missing) + "."
        )

    for name, definition in properties.items():
        if not isinstance(name, str) or not name:
            raise SchemaError("Os nomes em 'properties' devem ser textos não vazios.")
        _validate_property(name, definition)
    return schema


def _validate_property(name: str, definition: Any) -> None:
    if not isinstance(definition, dict):
        raise SchemaError(f"A propriedade '{name}' deve ser um objeto de definição.")
    _reject_unknown_keys(definition, PROPERTY_KEYS, f"propriedade '{name}'")

    field_type = definition.get("type")
    if field_type in SCALAR_TYPES:
        if "items" in definition:
            raise SchemaError(f"A propriedade escalar '{name}' não pode usar 'items'.")
        return
    if field_type != "array":
        raise SchemaError(
            f"A propriedade '{name}' deve ter tipo string, number, integer, boolean ou array."
        )

    items = definition.get("items")
    if not isinstance(items, dict):
        raise SchemaError(f"O array '{name}' deve declarar 'items' como objeto.")
    _reject_unknown_keys(items, {"type", "description"}, f"items de '{name}'")
    if items.get("type") not in SCALAR_TYPES:
        raise SchemaError(f"Os itens do array '{name}' devem ter tipo escalar suportado.")


def _reject_unknown_keys(value: dict[str, Any], allowed: set[str], location: str) -> None:
    unsupported = sorted(set(value) - allowed)
    if unsupported:
        raise SchemaError(
            f"Construções não suportadas em {location}: " + ", ".join(unsupported) + "."
        )
