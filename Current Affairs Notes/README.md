# Current Affairs Notes

Open `index.html` to browse the notes offline. Subjects and year/month/day groups are collapsed initially; search finds matching topics and facts. Each topic has editable Markdown, Previous/Next navigation, and Print / Save as PDF.

Repeated topics are consolidated in one file. Dates within a topic identify developments and dated statistics. `Topics.json` holds the reviewed content; `Processing Log.json` records which daily PDFs have been reviewed. A pending entry is not completed notes. Missing dates do not necessarily mean a daily issue was published.

Each subject has `PYQ-Prelim.json` and `PYQ-Mains.json`. Coaching practice questions are not presented as UPSC PYQs.

The working collection is on the external drive at `Current Affairs/Notes`. This directory is a portable Git snapshot containing authored notes and review metadata only. Downloaded PDFs and original attachments are excluded.

Rebuild the working notes with `python3 tools/build_current_affairs_notes.py`; set `CA_SOURCE_ROOT` to the source collection directory if it moves. Then run `python3 tools/publish_current_affairs_notes.py` to refresh this snapshot. Edit the working Markdown files before rebuilding; the builder preserves those edits.

Notes and code are committed/pushed at seven-day issue-date boundaries. Review progress remains explicit while the full collection is being processed.
