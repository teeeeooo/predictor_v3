```yaml
record:
  date: 2026-07-13
  topic: ahri-variable-exact-point-allowlist
  tags: ahri210240, hspf2, variable-capacity, point-schema, correction
  memory_review: updated
  memory_reason: The distinction between full schema metadata and points consumed by variable HSPF2 is a durable public-input contract.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
```

# Change Reason

The full HSPF2 schema includes points not consumed by the variable-capacity
engine. Allowing those keys through normalization could make an ignored input
appear effective while H12/H22 standard fallback executed. This record
supersedes the AHRI variable point-boundary detail in
`2026-07-13-remaining-silent-fallback-closure.md`.

# Contract / Behavior Changed

Variable HSPF2 now accepts exactly required H01, H11, H1N, H2Int, H32, A2 and
optional H12, H22, H42, plus the active `A_Full -> A2` alias. Canonical and
alias matching remains case-insensitive and conflicting A2 values fail fast.

Full-schema H2V and cooling B2/C2/D2/E2, retired aliases, typos, unrelated
keys, and non-string keys now fail during normalization and calculation before
fallback selection. The full schema lookup API and product-local dual/triple
resolvers remain unchanged. Normal omission of H12/H22 still uses Eq. 11.185
and Eq. 11.44/11.50 respectively.

# Evidence And Verification

Focused AHRI, fallback, product-isolation, capability, and guard tests passed
155 tests. All standards refactor tests passed 126 tests. Local Calculator/
application-related pytest passed 1,053 tests with 834 deselected and two
expected xfails. Repository-wide local pytest passed 1,887 tests with two
expected xfails. No GitHub CI evidence was used. Changed-owner compilation,
structure, staged objective, and whitespace gates complete in the same commit
workflow.

# Changed Files

AHRI private HSPF2 point owner, exact allowlist runtime guards, active AHRI and
all-standards design docs, memory seed, report index, and this correction
record.

# Known Risks

Callers sending full-schema but variable-unused point keys now receive an
explicit error. This is the intentional compatibility break. Adding a future
variable point requires actual engine consumption, allowlist, resolution tests,
and formula or contract evidence together.
