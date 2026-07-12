```yaml
record:
  date: 2026-07-13
  topic: all-standards-core-refactor-closeout
  tags: calculator, en14825, iso16358, ks-c9306, brazil, architecture, refactor, closeout
  memory_review: updated
  memory_reason: Stable EN, ISO, and KS private-owner packages plus cwd-independent static resource resolution are long-lived Calculator architecture decisions.
```

# Change Reason

Every active non-AHRI Calculator standard route required architecture closeout
against the AHRI stable-facade reference without formula or contract changes.

# Contract / Behavior Changed

EN 14825, ISO 16358, and KS C 9306 now keep their established public facade
modules while private standard-local owners hold config, point resolution,
performance curves, seasonal loops, and result assembly. Brazil was verified as
already compliant and not rewritten. AS/NZS remains a disabled compatibility
path. Profile resources now resolve statically without relying on repo cwd.

No formula, expected value, config meaning, import path, public signature,
profile/capability/calculator ID, result/detail/diagnostics schema, rounding, or
exception behavior changed.

# Evidence And Verification

Focused evidence passed for EN (307), ISO/Brazil (480 with one expected xfail),
KS (214), and cwd/resource/capability routes (56). The complete Calculator
collection passed 1,246 tests with two expected xfails; repository-wide pytest
passed 1,810 tests with the same two expected xfails. Changed owners compiled.
The structure guard reported ten pre-existing warnings and no new warning; the
three standard-monolith warnings were removed. Staged whitespace and objective
change gates passed.

# Changed Files

Stable EN/ISO/KS facades, their private owner packages, the static Calculator
resource resolver, contract/owner/runtime tests, standard owner notes, governing
design/index, project log, memory seed, this record, and the report index define
the completed workstream.

# Known Risks

Facade private-helper delegation remains temporarily available because current
tests and EN application config projection rely on selected helpers. This is not
a public-engine import and should be retired only through a separately approved
contract migration. AS/NZS compatibility remains intentionally inactive. No
formula-correction candidate was found.
