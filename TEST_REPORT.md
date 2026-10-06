# Billo SMS — Final Test Report

This build was tested locally against the actual Python-only server included in the package. Testing was split into two independent UI suites so the Default UI and New UI counts/results could be checked separately.

## Suite A — Billo Original UI

- Login + dynamic CAPTCHA: PASS
- Owner session: PASS
- Manager session: PASS
- Agent session: PASS
- Client session: PASS
- Default UI remained `reference-ui` OFF: PASS
- Dashboard loads: PASS
- My Ranges / My Numbers routes: PASS
- SMS CDR route: PASS
- CDR Date/Time filters: PASS
- CDR Range/Client/Number/CLI filters: PASS
- CDR role columns: PASS
- API incoming route: PASS
- Duplicate `sms_id` protection: PASS
- Country separation checks: PASS
- Allocation chain Owner → Manager → Agent → Client: PASS
- Current-holder CDR routing: PASS
- 0.01 per-OTP rate snapshot: PASS
- Client 1 OTP / Agent 1 OTP / Manager 1 OTP / Owner 1 OTP: PASS
- After 2 test OTPs: Client 2 / Agent 2 / Manager 2 / Owner 2: PASS
- After 2 test OTPs: Client $0.0200 / Agent $0.0200 / Manager $0.0200 / Owner $0.0200: PASS
- Background music only: PASS
- Click/tap sound effects: REMOVED / NOT USED
- Header UI switch visible: PASS

## Suite B — New UI

- New UI selected from visible header switch: PASS
- Centered three-line menu button: PASS
- Feature-card dashboard layout: PASS
- Owner feature cards include Dashboard, My Ranges, Create Manager, Create Agent, Create Client: PASS
- Manager create options limited to Agent + Client: PASS
- Agent create option limited to Client: PASS
- Client dashboard feature set limited to Dashboard, My Numbers, Statistics, SMS CDR: PASS
- New UI styling applied to authenticated pages: PASS
- SMS overview cards (Today SMS / Last 7 Days SMS / Last 30 Days SMS): PASS
- Local time/date: PASS
- Database-driven graph: PASS
- SMS CDR reference controls: PASS
- CDR role columns: PASS
- API incoming route: PASS
- Duplicate `sms_id` protection: PASS
- Country separation checks: PASS
- Allocation hierarchy: PASS
- 0.01 rate propagation: PASS
- Client 1 / Agent 1 / Manager 1 / Owner 1: PASS
- Client 2 / Agent 2 / Manager 2 / Owner 2: PASS
- Client/Agent/Manager/Owner $0.0200 after 2 OTPs: PASS
- Background music only: PASS
- Click/tap sound effects: REMOVED / NOT USED
- Persistent floating audio control: REMOVED

## Data integrity

- Test data was created only in isolated temporary test databases.
- No test users, numbers, OTPs, carriers or allocations are included in the final ZIP.
- CDR rate snapshots are stored additively and do not require destructive migration.
- Range/user deletion behavior remains non-destructive for history.

## Environment note

The supplied package uses the uploaded source's Python standard-library server architecture. Flask/SQLAlchemy packages were not installed in the test environment, so this report does not claim Flask runtime testing. The included server itself was executed and tested over HTTP locally.
