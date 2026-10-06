# Billo SMS — MASTER-based Python deployment

Start:
```bash
python3 run.py
```

This build preserves the uploaded Billo light/colorful UI as the default interface and adds the requested functional updates.

## Default UI
Billo Original remains the default: white/light professional layout, Billo branding, cat watermark, blue/pink/green/orange cards, compact responsive layout, profile photo and existing navigation language.

## Added
- Live 12-hour local clock with seconds and date.
- Real database 30-day SMS/OTP graph; 30 days is a viewing window, not CDR retention.
- API Management for creating carrier API profiles, mapping fields, configuring allowed IPv4/IPv6/CIDRs, enabling/disabling and deleting configurations.
- `/api/sms/incoming` routing by current active allocation with duplicate `sms_id` protection.
- Change UI: Billo Original / New UI. The New UI follows the supplied mobile panel reference: centered three-line menu, large feature cards, statistics cards, graph and matching page styling. The default Billo Original UI remains the default.
- Theme-specific original audio loops and UI sound effects. Browser autoplay restrictions are handled with a first-interaction fallback.
- Profile photo and persistent UI preference.
- Role-scoped CDR columns and current-holder routing.

## CDR
CDR history is retained. The application does not run a 30-day CDR deletion job.

## API payload
Carrier mapping supports `from`, `to`, `message`, and `sms_id` by configurable field names. The public callback is:
`/api/sms/incoming?carrier_id=ID`

## Database
SQLite is used by this uploaded-source build. Database initialization/migration is additive and does not intentionally drop or truncate existing data.

## Environment
`PORT`, `OWNER_USERNAME`, and `OWNER_PASSWORD` can be supplied as environment variables. For production, set credentials through the hosting environment instead of relying on source defaults.


### Latest UI update
- The moon/sun header control was replaced with a visible UI switch icon.
- New UI is selected from the header switch and applies to every authenticated page, not only Dashboard.
- Client access in the panel is limited to Dashboard, My Numbers, Statistics and SMS CDR.
- SMS CDR has From/To Date & Time, Range, Client, Number and CLI filters plus report/export controls.
- CDR stores a rate snapshot per accepted SMS so a 0.01 payout remains auditable for Client, Agent, Manager and Owner reporting.
- Vampire Mode and click/tap sound effects were removed.
