# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

## Guard Policy

<!-- Project-specific. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

<!-- Project-specific specialisation. -->

## Code Style

<!-- Project-specific specialisation. -->

## Tech Stack

<!-- Technology choices locked for this project. -->

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: NEVER [behavior] (affirmed [date]) -->
<!-- Example: NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

- NEVER fill Phần III of the AMLD Mẫu số 01 form. (affirmed 2026-10-09)

- NEVER submit a report when a required attachment (Bảng kê, Minh Họa Dòng (affirmed 2026-10-09)

Tiền.pdf, or Hồ sơ mở tài khoản) is missing — email a FAIL status instead. (affirmed 2026-10-09)

- NEVER proceed past a tick-box section (Phần IV/V) whose selected value falls (affirmed 2026-10-09)

outside the defined set — stop the customer flow and email an error. (affirmed 2026-10-09)

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

- ALWAYS read secrets (AMLD Portal, Accuity, Tax Authority, email) from (affirmed 2026-10-09)

environment variables or a secrets manager, never hardcoded. (affirmed 2026-10-09)

- ALWAYS retry a failed report-entry step up to 3 times, then hand the customer (affirmed 2026-10-09)

off to a backup robot when the error persists. (affirmed 2026-10-09)

- ALWAYS send a batch status email on completion to the report author (To), with (affirmed 2026-10-09)

Cc to qtrrhd@mbbank.com.vn, tamdp.ho@mbbank.com.vn, hanhnt1.ho@mbbank.com.vn, (affirmed 2026-10-09)

attaching the per-customer status file. (affirmed 2026-10-09)

- ALWAYS validate required files in each customer CIF folder before data entry (affirmed 2026-10-09)

and record the names of any missing files. (affirmed 2026-10-09)

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->

- Gỡ ràng buộc LOG_DONE: robot KHÔNG dùng cơ chế LOG_DONE; tín hiệu một lô sẵn sàng đến từ message Kafka topic RPA_STR_NHNN_INPUT. (learned 2026-10-09)

- Cấu hình & secrets (user/pass, endpoint, đường dẫn) đọc từ file data/config.yaml (KHÔNG dùng biến môi trường/secrets manager cho dự án local này); vẫn không hardcode trong mã, config.yaml không commit (gitignore), không log giá trị secret. Điều này điều chỉnh rule "ALWAYS read secrets from environment variables or a secrets manager" cho dự án này. (learned 2026-10-09)
