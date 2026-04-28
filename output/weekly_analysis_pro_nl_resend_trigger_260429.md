# Dutch companion resend trigger

This file intentionally matches the GitHub Actions path filter but does not match the production report filename regex.

Purpose: trigger the send-weekly-report workflow after the matched pair already exists:
- output/weekly_analysis_pro_260428.md
- output/weekly_analysis_pro_nl_260428.md

The delivery script should still select the latest canonical English pro report and its matching Dutch companion, not this trigger file.
