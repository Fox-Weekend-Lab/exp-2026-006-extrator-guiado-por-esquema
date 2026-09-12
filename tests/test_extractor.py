from types import SimpleNamespace

import pytest

from schema_guided_extractor.extractor import ExtractionError, extract_response


class FakeClient:
    def __init__(self, content):
        self.content = content
        self.calls = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


def test_extract_response_sends_json_instruction_and_decodes_result():
    client = FakeClient('{"data": {"name": "Ana"}, "evidence": {"name": ["Ana"]}}')
    result = extract_response(client, "Ana chegou.", {"type": "object", "properties": {}}, "chosen-model")
    assert result["data"]["name"] == "Ana"
    assert client.calls[0]["response_format"] == {"type": "json_object"}
    assert "evidence" in client.calls[0]["messages"][0]["content"]


def test_extract_response_rejects_non_json_content():
    with pytest.raises(ExtractionError, match="não é JSON"):
        extract_response(FakeClient("not json"), "texto", {"type": "object", "properties": {}}, "chosen-model")
