import json

from app.data.quote_store import QuoteStore


def test_custom_quotes_are_added_and_deleted(tmp_path):
    base_path = tmp_path / "quotes.json"
    custom_path = tmp_path / "custom_quotes.json"
    base_path.write_text(
        json.dumps([{"id": "built_in", "text": "内置", "category": "mind"}]),
        encoding="utf-8",
    )
    store = QuoteStore(base_path, custom_path, None)

    quote = store.add_quote("  回到呼吸。  ", "breath")

    assert quote["text"] == "回到呼吸。"
    assert [item["text"] for item in store.load_quotes()] == ["内置", "回到呼吸。"]
    assert store.delete_quote(quote["id"])
    assert store.load_custom_quotes() == []


def test_invalid_custom_quote_file_does_not_hide_built_ins(tmp_path):
    base_path = tmp_path / "quotes.json"
    custom_path = tmp_path / "custom_quotes.json"
    base_path.write_text(json.dumps([{"id": "a", "text": "A"}]), encoding="utf-8")
    custom_path.write_text("not-json", encoding="utf-8")

    assert QuoteStore(base_path, custom_path, None).load_quotes() == [{"id": "a", "text": "A"}]
    assert custom_path.with_suffix(".broken.json").exists()


def test_invalid_custom_quote_structure_is_backed_up(tmp_path):
    base_path = tmp_path / "quotes.json"
    custom_path = tmp_path / "custom_quotes.json"
    base_path.write_text("[]", encoding="utf-8")
    custom_path.write_text('{"text": "not-a-list"}', encoding="utf-8")

    store = QuoteStore(base_path, custom_path, None)

    assert store.load_custom_quotes() == []
    assert custom_path.with_suffix(".broken.json").exists()
