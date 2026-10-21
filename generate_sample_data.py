"""Helper to create a realistic test folder for showcasing LazyDesk AI capabilities."""
import shutil
from pathlib import Path
from core.config import APP_DIR

def create_sample_messy_folder(target_dir: Path = None) -> Path:
    """Create a realistic messy directory with documents, images, duplicates, and code."""
    if target_dir is None:
        target_dir = APP_DIR / "sample_messy_desktop"

    if target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Documents with rich text & action items
    (target_dir / "Q3_Strategic_Roadmap.md").write_text(
        "# Q3 Strategic Product Roadmap\n\n"
        "This document defines our key milestones and architectural deliverables for Q3.\n"
        "The primary focus is migrating from centralized services to local-first privacy models.\n\n"
        "## Key Action Items\n"
        "- [ ] TODO: Finalize offline encryption model specifications.\n"
        "- [ ] Must complete privacy audit before November 15, 2026.\n"
        "- [ ] Action: Benchmark local Gemma and Qwen inference throughput.\n"
        "- [ ] Review user consent telemetry by 2026-11-20.\n\n"
        "## Deadlines & Timeline\n"
        "- Phase 1 Architecture freeze: 2026-10-28\n"
        "- Security sign-off deadline: 2026-11-10\n"
        "- Release v2.0 Candidate: 2026-12-05\n"
    )

    (target_dir / "Vendor_Agreement_Draft_v2.txt").write_text(
        "CONFIDENTIAL SERVICE AGREEMENT\n\n"
        "This Service Agreement is entered into between CoreWorks LLC and Client Partner.\n"
        "The vendor shall provide cloud and edge deployment support starting on 2026-11-01.\n\n"
        "Deliverables and Obligations:\n"
        "- Must submit monthly compliance reports on the 1st of each month.\n"
        "- TODO: Sign master NDAs with all subcontracted engineers.\n"
        "- Action required: Confirm billing reconciliation schedule before 2026-11-12.\n"
        "- Final audit scheduled for 2026-12-20.\n"
    )

    (target_dir / "Meeting_Notes_Oct_2026.txt").write_text(
        "Weekly Engineering Standup - October 2026\n"
        "Attendees: Design Lead, Frontend Engineer, AI Systems Architect.\n\n"
        "Summary:\n"
        "We reviewed the Warm Paper and Forest Graphite theme implementation.\n"
        "The team agreed on minimal borders, calm contrast, and zero neon accents.\n\n"
        "Todos:\n"
        "- Need to verify contrast ratio on table headers.\n"
        "- Ensure undo preserves physical folder paths on disk.\n"
        "- Next review date: 2026-10-25.\n"
    )

    # 2. Spreadsheets
    (target_dir / "FY26_Budget_Forecast.csv").write_text(
        "Department,Q1,Q2,Q3,Q4,Total\n"
        "Engineering,120000,140000,165000,180000,605000\n"
        "Design,45000,50000,55000,60000,210000\n"
        "Infrastructure,30000,35000,42000,45000,152000\n"
        "Security,20000,22000,28000,30000,100000\n"
    )

    (target_dir / "Hardware_Procurement.csv").write_text(
        "Item,Quantity,UnitCost,Vendor,Date\n"
        "Mac Studio M2 Ultra,2,3999,Apple,2026-09-15\n"
        "Dell 32-inch 4K Monitor,4,699,Dell,2026-09-18\n"
        "Mechanical Keyboards,6,120,Keychron,2026-09-22\n"
    )

    # 3. Code files
    (target_dir / "benchmark_inference.py").write_text(
        "# Benchmark inference latency\n"
        "import time\n"
        "def benchmark():\n"
        "    t0 = time.time()\n"
        "    # Simulated token evaluation\n"
        "    return time.time() - t0\n"
    )

    (target_dir / "schema_migration_v3.sql").write_text(
        "-- Schema migration for activity history\n"
        "CREATE INDEX IF NOT EXISTS idx_activity_ts ON activity_log(timestamp);\n"
        "CREATE INDEX IF NOT EXISTS idx_scanned_cat ON scanned_files(category);\n"
    )

    # 4. Images / screenshots
    sample_png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 50
    (target_dir / "Screenshot 2026-10-18 at 14.22.01.png").write_bytes(sample_png_header)
    (target_dir / "Screenshot 2026-10-19 at 09.11.45.png").write_bytes(sample_png_header + b"123")
    (target_dir / "IMG_88291_Whiteboard.jpg").write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 60)

    # 5. Duplicates (exact identical content with duplicate hash signatures)
    dup_content = (
        "# LazyDesk AI Architecture & Annual Performance Report 2026\n\n"
        "Executive Summary:\n"
        "This report outlines desktop performance benchmarks, memory efficiency, and storage reduction.\n\n"
        "Key Deliverables:\n"
        "- Complete local privacy certification by 2026-11-30.\n"
        "- Deliver final binary releases to distribution mirrors by 2026-12-15.\n"
        "- TODO: Deprecate cloud telemetry and enforce local storage only.\n"
    )
    (target_dir / "Annual_Report_2026_Final.md").write_text(dup_content)
    (target_dir / "Annual_Report_2026_Final (1).md").write_text(dup_content)
    (target_dir / "Annual_Report_Copy_Backup.md").write_text(dup_content)

    return target_dir

if __name__ == "__main__":
    p = create_sample_messy_folder()
    print(f"Sample test workspace generated at: {p}")
