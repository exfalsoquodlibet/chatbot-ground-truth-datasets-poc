# Tests

Comprehensive test suite using pytest for the chatbot ground truth datasets POC.

## Running Tests

**Run all tests:**
```bash
uv run pytest
```

**Run with verbose output:**
```bash
uv run pytest -v
```

**Run specific test file:**
```bash
uv run pytest tests/test_models.py
```

**Run specific test class:**
```bash
uv run pytest tests/test_convert_csv_to_jsonl.py::TestCsvToJsonl
```

**Run specific test:**
```bash
uv run pytest tests/test_models.py::TestJailbreakGuardrailItem::test_valid_instance_false_outcome
```

## Test Coverage

### `test_models.py`
Tests for Pydantic models:
- Valid model instances
- Field validation
- Type conversions (string to boolean)
- Missing fields error handling
- Serialization (`model_dump()`)

### `test_convert_csv_to_jsonl.py`
Tests for CSV to JSONL conversion:
- Component name inference from paths
- Row parsing with Pydantic models
- CSV to JSONL conversion (dry-run and actual)
- Invalid CSV handling (bad values, wrong headers)
- Git diff parsing for changed files
- GitHub Actions environment variable usage
