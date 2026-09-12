"""Interface de linha de comando do extrator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .extractor import ExtractionError, create_client, extract_response, get_api_key, get_model
from .schema import SchemaError, validate_schema
from .validator import validate_response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extrai e valida dados estruturados de um texto.")
    parser.add_argument("--text", required=True, help="Caminho do arquivo de texto UTF-8.")
    parser.add_argument("--schema", required=True, help="Caminho do arquivo de esquema JSON.")
    parser.add_argument("--output", required=True, help="Caminho do relatório JSON de saída.")
    parser.add_argument("--model", help="Modelo a usar; sem esta opção, usa OPENAI_MODEL.")
    parser.add_argument("--response", help="Resposta JSON previamente salva para validação local.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = _read_text(args.text, "texto")
        schema = validate_schema(_read_json(args.schema, "esquema"))
        if args.response:
            response = _read_json(args.response, "resposta")
        else:
            api_key = get_api_key()
            model = get_model(args.model)
            response = extract_response(create_client(api_key), text, schema, model)
        report = validate_response(text, schema, response)
        _write_json(args.output, report)
    except (OSError, json.JSONDecodeError, SchemaError, ExtractionError) as error:
        print(f"Erro: {error}")
        return 2

    if report["errors"]:
        print("A validação encontrou erros; consulte o relatório JSON.")
        return 1
    print("Relatório gerado com sucesso.")
    return 0


def _read_text(path_string: str, label: str) -> str:
    path = Path(path_string)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise OSError(f"Arquivo de {label} não encontrado: {path}. Informe um caminho existente.") from error
    except UnicodeDecodeError as error:
        raise OSError(f"O arquivo de {label} deve estar codificado em UTF-8.") from error


def _read_json(path_string: str, label: str) -> object:
    content = _read_text(path_string, label)
    try:
        return json.loads(content)
    except json.JSONDecodeError as error:
        raise json.JSONDecodeError(
            f"O arquivo de {label} contém JSON inválido: {error.msg}", error.doc, error.pos
        ) from error


def _write_json(path_string: str, report: dict[str, object]) -> None:
    path = Path(path_string)
    try:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except FileNotFoundError as error:
        raise OSError(
            f"O diretório de saída não existe para {path}. Crie o diretório ou informe outro caminho."
        ) from error
