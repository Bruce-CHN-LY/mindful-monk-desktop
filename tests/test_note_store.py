import json

from app.data.note_store import NoteStore


def test_note_store_adds_text_and_deletes_by_index(tmp_path):
    path = tmp_path / "notes.json"
    store = NoteStore(path)

    note = store.add_note(" 急 ", " 先做眼前这一件事 ")

    assert note["id"]
    assert note["tag"] == "急"
    assert note["text"] == "先做眼前这一件事"
    assert store.load_notes() == [note]
    assert store.delete_note_at(0)
    assert store.load_notes() == []


def test_note_store_keeps_legacy_records_compatible(tmp_path):
    path = tmp_path / "notes.json"
    legacy = {"timestamp": "2026-06-18T10:00:00", "tag": "散"}
    path.write_text(json.dumps([legacy], ensure_ascii=False), encoding="utf-8")

    store = NoteStore(path)

    assert store.load_notes() == [legacy]
    assert store.delete_note_at(0)


def test_note_store_rejects_invalid_delete_index(tmp_path):
    store = NoteStore(tmp_path / "notes.json")

    assert not store.delete_note_at(0)


def test_note_store_preserves_invalid_file_as_backup(tmp_path):
    path = tmp_path / "notes.json"
    path.write_text("not-json", encoding="utf-8")

    store = NoteStore(path)

    assert store.load_notes() == []
    assert path.with_suffix(".broken.json").read_text(encoding="utf-8") == "not-json"
    assert not path.exists()


def test_note_store_filters_invalid_list_entries(tmp_path):
    path = tmp_path / "notes.json"
    note = {"timestamp": "2026-06-18T10:00:00", "tag": "稳"}
    path.write_text(json.dumps([note, "invalid"]), encoding="utf-8")

    assert NoteStore(path).load_notes() == [note]
