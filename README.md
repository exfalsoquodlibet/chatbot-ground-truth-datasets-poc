# Chatbot Ground-Truth Datasets

A version-controlled repository for human-labeled ground-truth datasets used to evaluate and test chatbot components. This POC demonstrates a workflow for managing immutable, versioned datasets with automated validation and format conversion.

## Overview

This repository provides:
- **Versioned CSV datasets** as the source of truth
- **Automated JSONL generation** from CSV files
- **Immutability enforcement** for published dataset versions
- **Validation workflows** to ensure data quality and proper versioning
- **Pydantic models** for schema validation

## Repository Structure

```
.
├── .github/workflows/        # GitHub Actions workflows
├── components/               # Dataset components
│   └── jailbreak_guardrail/
│       ├── csv/             # Source CSV files (versioned)
│       │   └── v1/
│       └── jsonl/           # Auto-generated JSONL files
│           └── v1/
├── models/                   # Pydantic data models
│   └── jailbreak_guardrail.py
├── tests/                    # Pytest test suite
├── tools/                    # Conversion scripts
│   └── convert_csv_to_jsonl.py
└── pyproject.toml           # Python dependencies (uv)
```

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd chatbot-ground-truth-datasets-poc

# Install dependencies
uv sync

# Run tests
uv run pytest
```

### Converting CSV to JSONL

```bash
# Dry run (preview changes)
uv run python tools/convert_csv_to_jsonl.py --dry-run

# Actual conversion
uv run python tools/convert_csv_to_jsonl.py
```

## Workflows

This repository uses GitHub Actions to automate validation and conversion:

| File | Description |
| ---- | ----------- |
| `.github/workflows/check-immutability.yaml` | Prevents modifications to files in existing version folders, ensuring data immutability |
| `.github/workflows/pr-checklist.yaml` | Validates that PRs include required version_info.yaml and CHANGELOG.md updates |
| `.github/workflows/validate-csv.yaml` | Validates CSV to JSONL conversion using Pydantic models (dry-run) |
| `.github/workflows/generate-jsonl.yaml` | Automatically converts CSV files to JSONL format and commits results after merges to main |

### Workflow Triggers

- **check-immutability**: Runs on every PR (opened/synchronized)
- **pr-checklist**: Runs on every PR (opened/synchronized)
- **validate-csv**: Runs on every PR (opened/synchronized)
- **generate-jsonl**: Runs on push to `main` branch (when a PR is merged)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Adding new dataset versions
- Maintaining immutability
- Metadata requirements
- PR submission process

### Key Principles

1. **CSV files are the source of truth** - All datasets start as CSV
2. **JSONL files are auto-generated** - Never edit JSONL files manually
3. **Dataset versions are immutable** - Once published, versions cannot be modified
4. **Every version needs metadata** - Include `version_info.yaml` for each version
5. **Update CHANGELOG.md** - Document all version changes


### Adding a New Component

1. Create component directory structure:
   ```
   components/<component_name>/
   ├── csv/v1/
   └── jsonl/v1/
   ```

2. Create Pydantic model in `models/<component_name>.py`

3. Update `parse_row_with_model()` in `tools/convert_csv_to_jsonl.py`

5. Add tests in `tests/`
