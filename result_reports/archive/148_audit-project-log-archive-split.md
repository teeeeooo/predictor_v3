# Audit: Project Log Archive Split

**Goal:** Audit whether `project_log.md` should be split into an active milestone log and an archive, and propose a safe exact-move strategy.

**Scope:** Audit line count, heading distribution, date range, and archive structure candidates. No actual file modification or move.

**Non-goals:** No `project_log.md` edit, no archive directory creation, no log movement, no summary/archive lifecycle maintenance.

---

## Current State

| Metric | Value |
|--------|-------|
| Total lines | 1,361 |
| Policy header | 12 lines (lines 1–12) |
| Dated headings | 31 |
| Separators (`---`) | 24 |
| Date range | 2026-05-04 to 2026-05-23 |
| All entries in | May 2026 only |

### Heading Distribution by Date

| Date | Heading count | First line |
|------|---------------|------------|
| 2026-05-04 | 5 | 335, 347, 358, 375, 407 |
| 2026-05-05 | 7 | 435, 444, 483, 525, 551, 579, 606 |
| 2026-05-06 | 3 | 631, 667, 687 |
| 2026-05-07 | 1 | 687 |
| 2026-05-10 | 3 | 293, 317, 335 |
| 2026-05-11 | 1 | 974 |
| 2026-05-16 | 4 | 1001, 1033, 1045, 1056 |
| 2026-05-17 | 5 | 188, 232, 264, 278, 1067 |
| 2026-05-18 | 1 | 98 |
| 2026-05-19 | 1 | 63 |
| 2026-05-23 | 2 | 13, 30 |

### Active Entry Candidates (most recent)

- **2026-05-23 — Project Memory Delta workflow + seed staging** (lines 13–27)
- **2026-05-23 — Xfail cleanup + PyQt/Tkinter environment stabilization** (lines 30–61)
- **2026-05-19 — ISO16358-2 HSPF -7_ext fix + golden update** (lines 63–97)

These three entries cover the most recent process-rule and architecture changes and should remain in the active `project_log.md`.

---

## Archive Move Candidates

All dated headings from **2026-05-04** through **2026-05-18** (28 headings, ~1,200 lines) are candidates for archive. The exact move principle is: **no summarization, no rewriting, no deletion** — copy the full dated entry text as-is into the archive file.

---

## Archive Structure Candidates

### Candidate A: Monthly Archive Files

```
docs/archive/project_log/
├── project_log_2026-05.md
```

- **Contents:** All May 2026 entries moved exactly from `project_log.md`.
- **Active `project_log.md`:** Policy header (12 lines) + most recent 2–3 entries (~100–150 lines).

**Pros:**
- Easy to extend: June entries go to `project_log_2026-06.md`, July to `project_log_2026-07.md`, etc.
- File sizes remain bounded and predictable (~1,000–1,500 lines per month).
- Searching by month is straightforward (`rg` against a single file).
- Token leakage per read is capped at one month’s worth of logs.

**Cons:**
- Requires creating a new file each month.
- If a single month grows very large (e.g., 50+ entries), it may need sub-month splitting later.

### Candidate B: Single Historical Archive File

```
docs/archive/project_log/
├── project_log_history_2026-05.md
```

- **Contents:** All archived entries in one file.
- **Active `project_log.md`:** Policy header + most recent 2–3 entries.

**Pros:**
- Simple: only one archive file to manage initially.
- Low overhead for small projects.

**Cons:**
- Will grow indefinitely until another split is needed.
- Searching requires scanning the entire archive.
- Token leakage risk increases as the archive grows.
- Does not scale naturally; eventually requires a second split decision.

---

## Comparison Summary

| Dimension | Candidate A (Monthly) | Candidate B (Single) |
|-----------|----------------------|----------------------|
| Token leakage per read | Medium (one month) | High (grows over time) |
| Searchability | Good (month-targeted) | Poor (linear scan) |
| Future maintenance | Low (append new month file) | Medium (re-split later) |
| Scalability | Good | Poor |
| Initial complexity | Low | Lower |

---

## Recommendation

**Candidate A (Monthly archive files)** is recommended.

Reason: The project is already generating 30+ entries in a single month. At this rate, a single archive file would exceed 2,000–3,000 lines within two months, recreating the exact problem we are trying to solve. Monthly files keep each archive bounded and make future archive splits unnecessary.

---

## Suggested Split/Move Task Outline (for a follow-up task)

1. **Create directory:** `docs/archive/project_log/`
2. **Move exact text:** Copy all dated entries from 2026-05-04 through 2026-05-18 into `docs/archive/project_log/project_log_2026-05.md`, preserving full text, headings, and separators.
3. **Trim active file:** Remove the archived entries from `project_log.md`, leaving only:
   - Policy header (lines 1–12)
   - Latest 2–3 entries (2026-05-19, 2026-05-23 entries)
4. **Update policy header:** Add a one-line note: "과거 로그는 `docs/archive/project_log/` 월별 파일에서 확인한다."
5. **Update `ACTIVE_DOCUMENTS.md`:** Add `docs/archive/project_log/*.md` to Reference Snapshots or create a new Archive Docs section.
6. **Update `AGENT_TASK_ROUTER.md`:** In the Documentation Sync & Lifecycle Gate, add `docs/archive/project_log/` to the archive scope (read-only, exact move only).
7. **Commit:** Source change (project_log trim + policy update) and archive creation as separate commits or a single commit with clear message.
8. **No project_memory_seed.md change needed:** Seed sources reference summaries/reports, not `project_log.md` directly.

---

## Verification

- `wc -l project_log.md` → 1,361 lines.
- `grep -n "^## " project_log.md` → 31 dated headings.
- `grep -n "^---$" project_log.md` → 24 separators.
- No existing file in `docs/archive/project_log/` was created or modified during this audit.
- `project_log.md`, `ACTIVE_DOCUMENTS.md`, and `project_memory_seed.md` were not modified.

---

## Known Risks

- If the active `project_log.md` is trimmed too aggressively (only keeping 1–2 latest entries), early-month milestones may be lost from the quick-read view. Keeping the latest 2–3 entries mitigates this.
- Monthly archive files may accumulate over years. A yearly folder (`docs/archive/project_log/2026/`) could be introduced later if monthly files become too numerous.

---

## Project Memory Delta

```yaml
- type: open_question
  topic: project log archive split
  content: project_log.md has reached 1,361 lines with 31 dated headings spanning May 2026 only. Should it be split into an active milestone log and monthly archive files under docs/archive/project_log/ to reduce token leakage while preserving exact historical text?
  keywords:
    - project-log
    - archive-split
    - token-leakage
    - milestone-log
    - exact-move
  assertionStatus: inferred
  source: result_reports/active/148_audit-project-log-archive-split.md
```
