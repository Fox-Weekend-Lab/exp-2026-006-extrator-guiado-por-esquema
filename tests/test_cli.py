import json

from schema_guided_extractor import cli


def test_cli_local_response_writes_report_without_remote_call(tmp_path, monkeypatch):
    text = tmp_path / "text.txt"
    schema = tmp_path / "schema.json"
    response = tmp_path / "response.json"
    output = tmp_path / "report.json"
    text.write_text("Ana tem 30 anos.", encoding="utf-8")
    schema.write_text(
        json.dumps({"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
        encoding="utf-8",
    )
    response.write_text('{"data": {"name": "Ana"}, "evidence": {"name": ["Ana"]}}', encoding="utf-8")
    monkeypatch.setattr(cli, "extract_response", lambda *args: (_ for _ in ()).throw(AssertionError("remote")))

    code = cli.main(["--text", str(text), "--schema", str(schema), "--response", str(response), "--output", str(output)])

    assert code == 0
    assert json.loads(output.read_text(encoding="utf-8"))["errors"] == []


def test_cli_reports_missing_api_key_before_remote_call(tmp_path, monkeypatch, capsys):
    text = tmp_path / "text.txt"
    schema = tmp_path / "schema.json"
    text.write_text("texto", encoding="utf-8")
    schema.write_text('{"type": "object", "properties": {}}', encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    code = cli.main(["--text", str(text), "--schema", str(schema), "--output", str(tmp_path / "report.json")])

    assert code == 2
    assert "OPENAI_API_KEY" in capsys.readouterr().out
