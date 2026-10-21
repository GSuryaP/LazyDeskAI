*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19)*

## What I Built

Tomorrow is International Sloth Day, and let's face it: **sloths have life figured out.** They don’t sprint through mundane, repetitive drudgery; they conserve their energy for what truly matters.

For most developers, students, and knowledge workers, our **Downloads** and **Desktop** folders are digital wastelands:
- Months of unread PDF invoices, contracts, and study notes.
- Duplicated presentations and reports named `Annual_Report_Final (1).md` wasting storage.
- Random screenshots and code snippets scattered across directories.

We know we should organize them, extract the action items, and clear out gigabytes of duplicates—but we keep putting it off.

**LazyDesk AI** rewards your inner sloth. It is a calm, local-first productivity assistant that does the computer chores you keep putting off:

1. **Intelligent Folder Sorting**: Scans messy directories in seconds and classifies files into dedicated categories (`Documents/`, `Spreadsheets/`, `Images/`, `Code/`, `Audio_Video/`, `Archives/`) with automatic collision protection (e.g. proposing `report_1.pdf` instead of overwriting).
2. **Local Document Intelligence**: Uses **Google Gemma 2 (2B)** running 100% on-device to digest multi-page documents, synthesize 2-sentence executive summaries, extract actionable to-do checklists, and detect upcoming calendar deadlines.
3. **Cryptographic Duplicate Detection**: Uses two-phase **SHA-256** checksum fingerprinting to detect exact identical copies, calculate reclaimable megabytes, and safely archive redundant copies without deleting the original.
4. **Physical Disk Undo**: Every move, rename, and archival is recorded in an atomic SQLite WAL-mode log. Clicking **"↩ Undo Move"** physically restores the file on your hard drive back to its original location.

---

## Demo

LazyDesk AI features a warm editorial design inspired by Claude and modern typography, offering two bespoke, contrast-tested themes:
- **Warm Paper (Light)**: Tactile cream background (`#F3F0E8`), soft cards (`#FAF8F2`), and deep forest green accents (`#496B50`).
- **Forest Graphite (Dark)**: Deep forest charcoal (`#18231F`), muted cards (`#202C25`), and soft sage highlights (`#A6C69A`).

### Key Workspaces in Action:
- **Overview Dashboard ("A little less to do.")**: An understated home view showing files scanned, pending organization suggestions, recoverable duplicate storage, and live Gemma engine latency (~5ms).
- **File Organizer**: Visual proposals with live filename search, category dropdown filters, collision warnings, and a safe **Dry Run Preview** before moving any files.
- **Document Intelligence**: An editorial reader that presents Google Gemma 2's executive summaries, checkboxes, and milestone dates with a 1-click clipboard copy button.
- **Duplicate Detection**: Sets grouped by SHA-256 hash, highlighting the preserved original in soft green and redundant copies in a safe archival queue.
- **Activity History**: Complete audit trail with real filesystem `↩ Undo Move` action.

*(Tip: Insert your project screenshots or a brief screen recording here showing Light & Dark mode).*

---

## Code

The complete source code, test suite, and quickstart documentation are available on GitHub:

{% github GSuryaP/LazyDeskAI %}

- **GitHub Repository**: [https://github.com/GSuryaP/LazyDeskAI](https://github.com/GSuryaP/LazyDeskAI)
- **License**: MIT
- **Tech Stack**: Python 3.10+, Streamlit, Google Gemma 2 (via Ollama), SQLite WAL, `pypdf`, `pytest`.

---

## How I Built It

LazyDesk AI is engineered with modular, production-grade Python components built around open-source AI:

- **Local Inference Engine (`core/llm_service.py`)**: Connects directly to local **Ollama** running **Google Gemma 2 (2B)**. It formats structured extraction prompts requesting JSON responses for executive summaries, to-dos, and date strings, with resilient heuristic fallbacks to ensure offline operation never hangs.
- **Document Extraction Pipeline (`core/doc_intel.py`)**: Extracts text from PDFs (`pypdf`), Markdown, text notes, and code, calculating word counts, line counts, and metadata before querying Gemma. Results are cryptographically cached in SQLite so re-reading a file is instantaneous.
- **Cryptographic Deduplicator (`core/duplicates.py`)**: Uses a two-stage filter: first clustering by exact byte size to eliminate 95% of unique files instantly, then computing full **SHA-256** checksums on matching sizes to guarantee zero false positives.
- **Safe Organizer & Collision Engine (`core/organizer.py`)**: Proposes clean folder routing. If a target file already exists, it calculates non-destructive incremental suffixes (e.g., `file_1.ext`) and alerts the user.
- **Transactional Audit Log & Physical Undo (`core/history.py` & `core/db.py`)**: Backed by SQLite in **WAL (Write-Ahead Logging)** mode. The `undo_operation` function reverses moves on the actual file system, safely recreating parent folders if necessary.
- **Editorial Design System (`ui/styles.py` & `ui/components.py`)**: Custom theme-token system rendering a responsive Streamlit layout with persistent Light/Dark state across browser refreshes.

---

## Why Does Open Innovation Matter?

The challenge prompt asks: *Does your open-based approach work better than a closed one? What did it make possible that a closed API wouldn't?*

For a personal desktop assistant, the answer is an emphatic **yes**. Building this tool with a proprietary cloud API (such as OpenAI or Anthropic) would be a fundamentally flawed product decision. Here is why open innovation is mandatory:

### 1. Absolute Air-Gapped Privacy
Your Desktop and Downloads folders contain your most private life: tax filings, bank statements, client NDAs, medical records, private keys, and personal photos.
- **Closed Cloud API**: Uploading the full text of every downloaded PDF or contract to a third-party cloud server introduces immense security and compliance liabilities.
- **Open-Source Gemma 2**: Google Gemma runs 100% on your machine. **Zero tokens ever leave your computer.** The application works flawlessly in airplane mode with no internet connection.

### 2. Zero Operating Cost
Closed APIs charge per thousand tokens. Running document analysis and OCR across hundreds of messy multi-page documents would quickly burn through expensive credits.
With open-weight Gemma running locally, organizing 10,000 files costs **$0.00 forever**.

### 3. True Model Sovereignty
Because LazyDesk AI interfaces with Ollama's open API standard, users have complete sovereignty. You can run lightweight `gemma2:2b` on a thin laptop, scale up to `gemma2:9b` or `gemma2:27b` on a workstation, or plug in a specialized fine-tune without changing a single line of application code.

---

## The Lazy Payoff

How much effort does LazyDesk AI actually save?

- **Before**: Spending 45 minutes every Friday clicking through a cluttered Downloads folder, manually dragging PDFs into folders, accidentally deleting duplicate invoices you might still need, and opening multi-page documents just to check if there was a deadline inside.
- **After**: One click on **"Scan Folder"**, one click on **"Execute Moves"**, and you have a structured, tidy workspace. In seconds:
  - 72 cluttered files sorted into categorized folders.
  - Duplicate sets safely archived into `_Duplicates_Archive/`, reclaiming disk space.
  - Important deadlines and to-dos extracted onto your dashboard by Gemma 2.
  - Any accidental move reversible via the **↩ Undo Move** button.

That is the true spirit of International Sloth Day: **Do the smart work once, and let local open-source AI handle the rest.**

---

## Prize Categories

- **Primary Category**: **Best Use of Gemma ($200 USD)**  
  *(LazyDesk AI uses Google's open-weight Gemma 2 model running locally on-device to power its document intelligence, executive summarization, action item extraction, and milestone date parsing with zero cloud latency and 100% air-gapped privacy).*
- **Overall Challenge**: **Week 3 Winner ($250 USD)**

---

*Built with Google Gemma 2, Streamlit, and Python for the Hacktoberfest 2026 DEV Challenge.*
