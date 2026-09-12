"""Construção da solicitação ao modelo e processamento de sua resposta."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


class ExtractionError(RuntimeError):
    """Indica falha ao obter ou interpretar a resposta do modelo."""


def get_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ExtractionError(
            "A variável de ambiente OPENAI_API_KEY é necessária para a extração remota. "
            "Defina-a ou use --response para validação local."
        )
    return api_key


def get_model(argument_model: str | None) -> str:
    model = argument_model or os.environ.get("OPENAI_MODEL")
    if not model:
        raise ExtractionError(
            "Informe --model ou defina a variável de ambiente OPENAI_MODEL para a extração remota."
        )
    return model


def build_prompt(text: str, schema: dict[str, Any]) -> str:
    serialized_schema = json.dumps(schema, ensure_ascii=False, indent=2)
    return (
        "Extraia informações do texto conforme o esquema fornecido. Responda somente com um "
        "objeto JSON válido no formato {\"data\": {...}, \"evidence\": {...}}. "
        "data deve conter os valores extraídos. evidence deve associar cada campo a uma lista "
        "de trechos literais do texto usados como evidência. Não invente trechos de evidência.\n\n"
        f"ESQUEMA:\n{serialized_schema}\n\nTEXTO:\n{text}"
    )


def create_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)


def extract_response(
    client: Any, text: str, schema: dict[str, Any], model: str
) -> dict[str, Any]:
    """Solicita uma resposta JSON ao cliente OpenAI já configurado."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": build_prompt(text, schema)}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as error:
        raise ExtractionError("A API retornou uma resposta em formato inesperado.") from error
    except Exception as error:
        raise ExtractionError("Não foi possível concluir a chamada ao modelo.") from error

    if not isinstance(content, str):
        raise ExtractionError("O modelo não retornou conteúdo textual em JSON.")
    try:
        decoded = json.loads(content)
    except json.JSONDecodeError as error:
        raise ExtractionError("O modelo retornou conteúdo que não é JSON válido.") from error
    if not isinstance(decoded, dict):
        raise ExtractionError("O modelo deve retornar um objeto JSON no contrato solicitado.")
    return decoded
