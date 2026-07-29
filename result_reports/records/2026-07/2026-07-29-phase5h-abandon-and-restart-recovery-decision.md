record:
  date: 2026-07-29
  topic: phase5h-abandon-and-restart-recovery-decision
  tags: train-admin, phase-5h, recovery-decision, abandon, private-attempt, locked-seal
  memory_review: updated
  memory_reason: The user-approved recovery disposition supersedes the prior actual-compute at-most-once direction and constrains the next source implementation.

# Change Reason

The seventh independent audit failed at exact head
`ed20d081ded7621b145ff95faa0e56e96163e303` despite successful historical
exact-head run `30421708922`. A visible final permit cannot distinguish every
pre- and post-directory-durability parent-death state or prove that Core work
occurred. Rather than add process adoption, a generic supervisor, or a complex
transactional coordinator, the user approved an explicit abandon-and-restart
product decision.

# Contract / Behavior Changed

- Never launch a replacement while the prior confirmation child is alive or
  liveness is uncertain.
- After proven child termination without complete official finalization,
  quarantine and abandon that private attempt. Start one new private attempt
  from the beginning under the same canonical confirmation identity.
- Never resume, append to, restore, or mix partial model, metric, manifest,
  staged Candidate, locked result, or terminal evidence. Quarantined artifacts
  remain non-official; retention owns any later deletion.
- Failure before locked-seal consumption follows normal abandon-and-restart.
  Consumed seal without complete durable locked result and finalization
  abandons the entire Confirmation; another evaluation requires a new seal and
  new Confirmation.
- Complete durable terminal confirmation and public Candidate pairs replay
  without abandonment or duplicate publication.
- The retained at-most-once boundaries are one simultaneously live
  Confirmation compute and one public Candidate/terminal finalization, not
  actual-compute at-most-once across sequential abandoned attempts.

# Superseded Direction

This decision supersedes earlier recovery wording that treated permit
existence as permanent proof of actual Core start, prohibited every sequential
retraining attempt after permit publication, or implied partial execution or
locked-result resume. Historical audit records remain unchanged as append-only
evidence of the contracts assessed at those heads.

# Verification

Documentation review distinguishes ordinary training failure from
post-consumption locked failure, quarantine from immediate deletion, and
completed-result replay from incomplete-attempt restart. Diff validation must
show documentation-only paths. Runtime source, tests, PR metadata, production
artifacts, migration state, and retention contents are unchanged.

# Next Step And Non-goals

The next action is a bounded Lane C source Worker implementing this contract in
the existing lifecycle, confirmation, process-adapter, training, and Candidate
owners. Fresh independent audit and merge occur only after source completion.
External daemons, generic process supervision, child adoption, production
confirmation/promotion, migration apply, retention/delete apply, destructive
cleanup, and audit approval remain excluded.
