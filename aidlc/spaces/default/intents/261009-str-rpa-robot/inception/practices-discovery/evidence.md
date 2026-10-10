# Evidence — Practices Discovery (Draft)

## Participants and what each inspected

- **Pipeline & Deploy lead (aidlc-pipeline-deploy-agent):** Drafted all five
  practice areas. Inspected the organisation defaults in
  `aidlc/spaces/default/memory/org.md` (Way of Working, Walking Skeleton,
  Testing Posture, Deployment, Code Style) and the US2 source document
  (`docs/08_US2_TomTat.md`) for project-specific hard constraints.
- Lead-only run: no blind support review was dispatched (the collaborators
  switch is off for the classic scope at this stage).

## Project type

- Greenfield. The workspace has no application code yet (no prior commit).
  Practices are drawn from org defaults as suggested starting points, specialised
  by the US2 requirements document.

## Source-derived constraints

- The US2 document states explicit robot rules that became draft hard
  constraints: retry ≤ 3 then failover; mandatory batch status email with fixed
  Cc list; LOG_DONE completion gating; required-file validation per CIF folder;
  do not fill Phần III; fail-closed on missing mandatory attachments and
  out-of-definition tick values.

## Interview decisions

- Q1 Way of Working: Gitflow (develop + release branches).
- Q2 Walking Skeleton: Yes — build a thin end-to-end slice first.
- Q3 Testing Posture: TDD (write tests first, then code).
- Q4 Deployment: Run locally on this machine; no multi-environment pipeline.
- Q5 Code Style: Language-idiomatic formatter + linter in CI before merge; lint
  failure blocks merge; secrets not hardcoded.
- Note surfaced to the human: Q1 (Gitflow) and Q4 (run locally) sit at different
  ends of the delivery spectrum; the choices were kept as affirmed, with the
  branching strategy acknowledged as heavier than a local-run robot strictly
  needs.

## Unresolved uncertainty

- Target implementation language, RPA framework/toolchain, and CI platform are
  not yet chosen; the code-style and testing tooling specifics are deferred to
  later stages.
- Non-functional load figures (customer growth, concurrency, transaction volume)
  are marked "chưa điền" in the source document and will need estimation in the
  NFR stage.
- Jira FCRM-6209 is marked Cancelled in the source; scope should be reconfirmed
  with the business owner.
