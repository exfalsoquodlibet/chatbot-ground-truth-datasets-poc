# Contributing to Chatbot Ground-Truth Datasets

Welcome! This repository contains the human-labeled **ground-truth datasets** for various govuk-chat components.  
This document describes how to:
- **add new dataset versions**
-  **maintain immutability**, and 
- **ensure proper metadata tracking**.

---

## Principles

1. **CSV files are the source of truth.**  
2. **JSONL files are generated automatically** via GitHub Actions after a PR is merged.  
3. **Dataset versions are immutable.** Once a version folder (e.g., `v1/`) is created, it must **never be edited**.  
4. **Per-version metadata** is required for each new dataset version.  
5. **Repo-level `CHANGELOG.md`** summarizes all versions and key changes.

---

## 1. Determine Version Bump

- Minor edits --> bump minor version: `v1.1`, `v2.1`  
- Major updates or schema changes --> bump major version: `v2`, `v3`  

> **Do not overwrite existing versions.** Immutability ensures reproducibility.

---

## 2. Create a New Version Folder

For the component you are updating, create a folder:

```
components/<component>/csv/vX.Y/
```

```
**Example:**
components/structured_answer_generation/csv/v1.1/
```

---

## 3. Export CSV from Google Sheets

1. Open the Google Sheet for the dataset.  
2. Make your edits collaboratively.  
3. Export the sheet as **CSV**.  
4. Save the CSV into the new version folder:

```
Example
components/<component>/csv/vX.Y/dataset.csv
```


---

## 4. Add Per-Version Metadata

Create a `version_info.yaml` in the same folder with the following fields:

```yaml
version: v1.1
date: 2026-01-06
changes:
  - Updated structured answers to reflect May 2025 content
  - Fixed labeling inconsistencies
notes: |
  None
```

```
Example
components/<component>/csv/vX.Y/dataset.csv
components/<component>/csv/vX.Y/version_info.yaml
```

Required fields:
- version: must match the folder name
- date: creation date
- changes: bullet list of main changes
- notes: optional free-text for extra context

This metadata is read by humans for auditing and extra context.

---
## 5. Update `CHANGELOG.md`

Add a summary of the new version in the repo-level changelog. For example:

```markdown
## Structured Answer Generation
- **v1.1** (2026-01-06): Updated structured answers to reflect May 2025 content; fixed labeling inconsistencies.


----

## 6. Open a Pull Request (PR)

1. Push your branch to GitHub.  
2. Open a PR targeting `main`.  
3. Use the following PR checklist:

- [ ] New version folder added (`dataset.csv` + `version_info.yaml`)  
- [ ] Old versions are untouched  
- [ ] `CHANGELOG.md` updated  
- [ ] CSV format consistent with schema  
- [ ] Optional: validation scripts run locally  

> > The GitHub Actions workflow will automatically:
> - Validate the CSV schema
> - Check for basic errors (empty fields, duplicates, required columns)
> - Convert the CSV into JSONL files and add them to the repo once merged

--- 
✅ Summary

- Decide version bump --> create new folder
- Export CSV --> save in folder
- Add version_info.yaml
- Update CHANGELOG.md
- Open PR --> review --> merge
- JSONL generated automatically

By following this workflow, all dataset versions remain reproducible, auditable, and clearly documented.

# GItHUb actions

1) when PR is open checks that CSV respects the schema (validation) [ci/cd test]
2) CSV Validation	PR open	Catch schema/format errors before merge
JSONL Generation	PR merge to main	Convert CSV → JSONL automatically
Prevent edits to old versions	PR open	Enforce immutability
PR Checklist automation	PR open	Ensure metadata & changelog included