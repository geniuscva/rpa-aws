# Team-Level Rules

> This team's affirmed practices and corrections. Loaded after `org.md` as
> strict-additive guidance; contradictions with broader policy are rejected.
> Populated by the practices-discovery affirmation gate. Edit at the gate,
> not directly.

## Way of Working

We use Gitflow: a long-lived `develop` integration branch and `release`
branches, with feature branches cut from `develop` and merged back via review.
Hotfixes branch from the release line as needed. Each unit of work is a feature
branch that integrates into `develop`; releases are stabilised on a `release`
branch before being tagged.

## Walking Skeleton

We don't run a walking skeleton for this project. The pipeline is linear
(ConsumeData → DataEntryAccuity → DataEntryTraCuuThue → DataEntryAMLD →
TongHopVaGuiMail) and the integration contract (StrRecord) is pinned at Contract
Design, so each unit is built fully and integrated against that shared contract
rather than proving a thin end-to-end slice first. (learned 2026-10-09, overrides
the earlier thin-slice-first statement.)

## Testing Posture

- **Methodology**: tdd
- **Methodology evidence**: The team affirmed test-driven development — write
  the test first, then the code that makes it pass. The STR robot's logic is
  specified by concrete source-file mappings and the seven acceptance scenarios,
  which translate cleanly into tests written ahead of implementation.
- **Ordering**: For each testable layer (file-ingestion and LOG_DONE checks,
  data aggregation and mapping, external lookups, portal form-fill, email
  notification), write the failing test first, then implement until it passes,
  then refactor.
- Coverage floor: 80% line coverage, run in CI before merge (classic scope
  default).
- Test types: unit tests for data-aggregation and mapping logic (cash-flow
  diagram counts, Phần IV/V derivation rules); integration/contract tests for
  folder-ingestion and LOG_DONE checks; scenario tests covering the seven
  acceptance scenarios (success, missing file, incomplete log, Accuity login
  failure, retry, failover, batch email).
- External systems (AMLD Portal, Accuity, Tax Authority) are mocked/stubbed in
  automated tests; live interaction is verified separately.

## Guard Policy

<!-- Affirmed by the team. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless project.md or the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

The robot runs locally on this machine. There is no multi-environment
deployment pipeline: no staging/production promotion, no CD. Running the robot
means executing it directly in this workspace's runtime. Any later move to a
managed environment is a separate decision, not assumed here.

## Code Style

We defer to project-level configuration: a language-idiomatic formatter and
linter run in CI before merge, with a failing lint blocking the merge. Naming
follows the chosen language's idiom. No project-wide rename rules unless the
team affirms one. Secrets (AMLD Portal, Accuity, Tax Authority, email
credentials) are never hardcoded — read from environment variables or a secrets
manager.
## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
