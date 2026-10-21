"""Comprehensive unit tests for core functionality of LazyDesk AI."""
import os
import shutil
import tempfile
from pathlib import Path
import pytest
from core.db import init_db, set_setting, get_setting, log_activity, get_activity_history
from core.scanner import scan_directory, categorize_file, compute_file_hash
from core.duplicates import find_duplicates, resolve_duplicates
from core.organizer import prepare_organization_plan, execute_organization_plan
from core.history import undo_operation
from core.doc_intel import extract_text_from_file
from core.llm_service import LLMService

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def temp_workspace():
    tmp_dir = tempfile.mkdtemp(prefix="lazydesk_test_")
    yield Path(tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)

def test_settings_and_db():
    set_setting("theme", "dark")
    assert get_setting("theme") == "dark"
    set_setting("theme", "light")
    assert get_setting("theme") == "light"

def test_file_categorization():
    assert categorize_file("invoice.pdf") == "Documents"
    assert categorize_file("budget.xlsx") == "Spreadsheets"
    assert categorize_file("photo.PNG") == "Images"
    assert categorize_file("script.py") == "Code"
    assert categorize_file("podcast.mp3") == "Audio & Video"
    assert categorize_file("backup.zip") == "Archives"
    assert categorize_file("unknown.xyz123") == "Others"

def test_scanner_and_organizer(temp_workspace):
    # Create sample files
    doc = temp_workspace / "report.pdf"
    doc.write_text("Test document content with deadline 2026-12-01.")
    img = temp_workspace / "photo.jpg"
    img.write_bytes(b"\xFF\xD8\xFF\xE0" + b"0" * 100)

    results = scan_directory(str(temp_workspace))
    assert len(results) == 2

    # Prepare plan
    plan = prepare_organization_plan(results, str(temp_workspace / "Organized"))
    assert len(plan) == 2

    # Execute plan
    success, fails, errors = execute_organization_plan(plan, dry_run=False)
    assert success == 2
    assert fails == 0

    # Verify moved to category subfolders
    assert (temp_workspace / "Organized" / "Documents" / "report.pdf").exists()
    assert (temp_workspace / "Organized" / "Images" / "photo.jpg").exists()

def test_duplicates_and_resolution(temp_workspace):
    # Create identical files
    f1 = temp_workspace / "original.txt"
    f2 = temp_workspace / "copy.txt"
    content = "Identical hash content 123456789"
    f1.write_text(content)
    f2.write_text(content)

    dups = find_duplicates(str(temp_workspace))
    assert dups["total_duplicates"] == 1
    assert len(dups["groups"]) == 1

    # Resolve duplicates by archiving
    dup_path = dups["groups"][0]["duplicates"][0]["path"]
    success, errors = resolve_duplicates([dup_path], action="archive")
    assert success == 1
    assert not Path(dup_path).exists()
    archive_folder = Path(dup_path).parent / "_Duplicates_Archive"
    assert archive_folder.exists()

def test_activity_undo(temp_workspace):
    file_a = temp_workspace / "doc_to_move.txt"
    file_a.write_text("Hello undo test")

    dest_folder = temp_workspace / "target_folder"
    dest_folder.mkdir()
    file_b = dest_folder / "doc_to_move.txt"

    shutil.move(str(file_a), str(file_b))
    act_id = log_activity("test_move", str(file_a), str(file_b), status="success", can_undo=True)

    assert not file_a.exists()
    assert file_b.exists()

    # Undo operation
    success, msg = undo_operation(act_id)
    assert success is True
    assert file_a.exists()
    assert not file_b.exists()

def test_doc_text_extraction(temp_workspace):
    txt_file = temp_workspace / "notes.txt"
    txt_file.write_text("Project milestone review.\nTODO: Finalize quarterly budget.\nDeadline: 2026-11-15.")

    res = extract_text_from_file(str(txt_file))
    assert res["error"] is None
    assert "Project milestone review" in res["text"]
    assert res["metadata"]["word_count"] > 0

def test_llm_service_fallback():
    llm = LLMService(host="http://localhost:99999") # intentionally invalid host for fallback test
    parsed = llm._parse_json_or_fallback(
        None,
        "Meeting notes.\nTODO: Deliver final report.\nDeadline: 2026-10-30.",
        "notes.txt"
    )
    assert parsed["summary"] is not None
    assert len(parsed["action_items"]) > 0
    assert any("Deliver final report" in a for a in parsed["action_items"])
    assert "2026-10-30" in parsed["key_dates"]
