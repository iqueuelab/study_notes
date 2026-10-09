# UPSC notes workflow

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
