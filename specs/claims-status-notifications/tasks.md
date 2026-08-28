# Tasks: Claim Status Notifications

1. Review the existing claim assessment flow in `src/dreamguard/claims.py` and confirm the supported statuses.
2. Define the notification contract for the four supported outcomes and capture the expected use of synthetic contact details.
3. Add a notification helper that maps each supported decision status to a clear client-safe message and supports optional synthetic contact details.
4. Export the helper and any related contact model from `src/dreamguard/__init__.py` so they are available through the public package API.
5. Document the helper and the notification contract in `docs/SERVICE.md` with an example that matches the current behavior.
6. Add unit tests covering approved, rejected, referred, and pending-documents outcomes, including the synthetic contact-details path.
7. Verify package-level exports and run the full test suite to confirm the implementation and its documentation examples remain consistent.
8. Produce a traceability review note that maps the intent, design, and tasks so gaps are visible before implementation proceeds.
