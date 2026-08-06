# Result Records

New durable result records are exceptional change-history artifacts, not a
required output for every task.

- New records: `records/YYYY-MM/YYYY-MM-DD-<slug>.md`
- Discovery index: `REPORT_INDEX.md`
- Long-term agent recall: `memory/project_memory_seed.md`
- Existing `active/`: legacy input retained at its historical path
- Existing archive and summary evidence: read-only `legacy/archive/` and
  `legacy/summaries/`

Do not read report bodies broadly. Search `REPORT_INDEX.md`, memory topics, or
stable keywords first, then open only the required record or legacy evidence.

For fast record discovery, filter the index before opening bodies:

- date/month: `rg '^\| 2026-08' result_reports/REPORT_INDEX.md`
- topic/tag: `rg -i 'result-review|windows|data-mapping' result_reports/REPORT_INDEX.md`
- combine filters: `rg '^\| 2026-08' result_reports/REPORT_INDEX.md | rg -i 'windows'`

The index row is the discovery unit; record directories are storage, not a topic
navigation hierarchy.

Legacy report and summary bodies preserve historical paths and commands and
must not be blanket-rewritten.
