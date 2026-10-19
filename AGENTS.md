# UPSC notes workflow

## Page styles

- Follow the user's manually updated styles for each page when adding or updating notes. Preserve each page type's existing layout, spacing, colours, typography, navigation and print rules; update its generator when needed so regeneration retains those choices.
- The latest current-affairs styles use a `1040px` main width and `20px` day-group indentation; follow newer manual changes if these evolve. Keep responsive and print overrides. Fix CSS syntax errors while preserving the intended appearance.

When creating or updating chapter notes from supplied images or documents:

- Make concise revision notes without omitting important facts; use diagrams readable on small screens and in print where useful.
- Maintain exactly two common PYQ JSON files at the subject folder level: `PYQ-Prelim.json` and `PYQ-Mains.json`. Append questions from all chapters to these files rather than creating chapter-specific JSON files.
- Each file contains `subject`, `exam_stage`, and a `questions` array. Each question must include the full `question`, its `chapter`, and integer `year`.
- Preserve all numbered statements and answer options for prelims questions. Include answers only when available. Do not include `source`, `sources`, or `answer_source` fields in PYQ JSON files.
- For mains, preserve subparts and marks/word limits when provided. Never invent questions or missing years; flag unknown years for review.
- Preserve existing questions and avoid duplicates by exam stage, year and question text. Keep an empty questions array if the supplied material contains no PYQs for that stage.
- Validate JSON after changes. Continue including useful PYQ revision explanations in chapter notes.

- Keep note headers to the chapter name only; do not add “UPSC Quick Revision”. Omit introductory production metadata such as image counts/names, printed page ranges, preparation/check dates, “editable Markdown accompanies these notes”, and statements about diagram print quality. Keep the Print / Save as PDF control and useful subject content/source references.

- Keep standalone end-of-chapter Article summaries in the common editable `Indian Polity/Articles Summary.md` and matching HTML preview. Merge new entries without duplicates; retain Article citations that explain chapter concepts, but do not reproduce standalone Article indices within individual chapter notes.

- Organise the common Articles Summary by constitutional Part in Part order, with Articles in ascending numeric order within each Part; keep lettered Articles and clauses beside their parent Article.

## Historical subject chronology

- When completing any history chapter (Modern Indian History, Ancient/Medieval India, Indian Art and Culture, or World History), update that subject’s common `Chronology.json`, editable `Chronology.md`, and responsive `Chronology.html` at subject-folder level. Start the file when the first chapter is completed; keep expanding it chapter by chapter.
- Include all dated historical events, reigns, treaties, wars, institutional changes and relevant background periods covered in the chapter. Exclude PYQ exam years, rejected dates and unsupported dates. Do not invent dates for undated events. Keep approximate/disputed dates clearly labelled.
- Maintain one entry for each event; merge chapter references and complementary facts when an event recurs. Retain previous entries. Store numeric start/end years and known month/day separately; use negative years for BCE. Sort chronologically by start date, preserve ranges, and do not imply an exact within-year sequence when only years are known.
- Keep chapter links, event/category and chapter filters, readable vertical timeline cards on small screens, and a clean A4 print layout. Preserve corrected facts and qualifications from the chapter notes. Regenerate Markdown/HTML with `python3 tools/build_history_chronology.py "<subject-folder>"` after editing the common JSON.

## Polity amendments summary

- Maintain the common editable `Indian Polity/Amendments Summary.md` and responsive `Amendments Summary.html` when completing Polity chapters. Group all amendment-related changes across chapters under one heading per constitutional amendment number, in ascending numeric order, with the Amendment Act title year. Merge complementary changes without duplicates and preserve earlier entries.
- Include relevant Articles/Parts/Schedules, before-and-after changes, and chapter links. Distinguish Act title year from assent/commencement; clearly label repeal, uncommenced provisions and judicial invalidation without treating them as operative law or invalidating a whole amendment when only part was struck down. Exclude ordinary statutory amendments and other countries’ amendments.

## Current affairs notes and Git checkpoints

- Process current-affairs notes one source day at a time, using one worker at a time to conserve credits (latest user instruction). Preserve existing larger-batch drafts and integrate only fully reviewed dates. Missing source dates require an explicit gap record, never invented notes. Push completed work when requested and retain the seven-day Git checkpoints below.
- Review downloaded daily PDFs chronologically, including their page images. Maintain one editable Markdown file and responsive HTML page per topic; merge repeated facts and add dated developments without duplicating whole sections.
- Keep the main index compact: collapsed subject groups, year/month/day browsing, search and subject filters. Preserve Previous/Next navigation and Print / Save as PDF. Print all relevant collapsed content by expanding it for printing and restoring the browsing state afterward.
- Current source collection is the external-drive `Current Affairs` folder reached through the local symlink. Build with `tools/build_current_affairs_notes.py`; override `CA_SOURCE_ROOT` if the collection moves.
- User authorises committing and pushing current-affairs notes/code to `origin` after each seven-day batch. Use weekly boundaries in issue-date order (1–7 January, 8–14 January, etc.); report gaps rather than silently treating absent PDFs as reviewed.
- Run `tools/publish_current_affairs_notes.py` to publish authored notes/HTML/PYQ JSON and review metadata into `Current Affairs Notes` in the checkout. The external Notes folder is the working master; the tracked folder is its portable snapshot. Never stage the `Current Affairs` symlink, downloaded source PDFs/images, original attachments, caches, AppleDouble files or blank directories.
- Validate JSON and staged paths before each commit. Push only completed material, retain progress metadata, and record the successful commit and next seven-day boundary in the external Operations checkpoint file.

## Shared notes home

- The root `index.html` is the offline entry point for subject chapters, common summaries and current-affairs topics. Rebuild it with `python3 tools/build_notes_home.py` after adding chapters or changing common summaries. The current-affairs publisher runs this builder automatically.
- Keep subjects and history units collapsible, search/filter both collections, and preserve the Study home return link on generated pages. Only completed notes belong in the hub; exclude source downloads and empty folders.
