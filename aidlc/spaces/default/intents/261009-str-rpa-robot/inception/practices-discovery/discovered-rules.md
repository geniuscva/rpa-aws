# Discovered Rules — Draft

> Hard constraints for the STR automation robot. Only human-stated or
> source-document-mandated constraints appear here, pending affirmation.

## Mandated

- ALWAYS read secrets (AMLD Portal, Accuity, Tax Authority, email) from
  environment variables or a secrets manager, never hardcoded.
- ALWAYS retry a failed report-entry step up to 3 times, then hand the customer
  off to a backup robot when the error persists.
- ALWAYS send a batch status email on completion to the report author (To), with
  Cc to qtrrhd@mbbank.com.vn, tamdp.ho@mbbank.com.vn, hanhnt1.ho@mbbank.com.vn,
  attaching the per-customer status file.
- ALWAYS verify the two LOG_DONE completion files (excel source + customer
  dossier) before processing a batch; stop the flow if either is missing.
- ALWAYS validate required files in each customer CIF folder before data entry
  and record the names of any missing files.

## Forbidden

- NEVER fill Phần III of the AMLD Mẫu số 01 form.
- NEVER submit a report when a required attachment (Bảng kê, Minh Họa Dòng
  Tiền.pdf, or Hồ sơ mở tài khoản) is missing — email a FAIL status instead.
- NEVER proceed past a tick-box section (Phần IV/V) whose selected value falls
  outside the defined set — stop the customer flow and email an error.
