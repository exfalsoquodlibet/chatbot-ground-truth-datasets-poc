import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.convert_csv_to_jsonl import (
    infer_component_from_path,
    parse_row_with_model,
    csv_to_jsonl,
    get_changed_csv_files,
)
from models.jailbreak_guardrail import JailbreakGuardrailItem


class TestInferComponentFromPath:
    """Test component name inference from file paths."""

    def test_valid_component_path(self):
        path = Path("components/jailbreak_guardrail/csv/v1/data.csv")
        assert infer_component_from_path(path) == "jailbreak_guardrail"

    def test_nested_component_path(self):
        path = Path("repo/components/my_component/csv/v2/test.csv")
        assert infer_component_from_path(path) == "my_component"

    def test_invalid_path_no_components(self):
        path = Path("data/csv/v1/test.csv")
        with pytest.raises(SystemExit):
            infer_component_from_path(path)


class TestParseRowWithModel:
    """Test Pydantic model parsing from CSV rows."""

    def test_valid_jailbreak_guardrail_row(self):
        row = {"question": "What is the capital?", "expected_outcome": False}
        model = parse_row_with_model(row, "jailbreak_guardrail")
        assert isinstance(model, JailbreakGuardrailItem)
        assert model.question == "What is the capital?"
        assert model.expected_outcome is False

    def test_valid_jailbreak_with_boolean_string(self):
        # pandas often reads booleans as strings
        row = {"question": "Test question", "expected_outcome": "true"}
        model = parse_row_with_model(row, "jailbreak_guardrail")
        assert model.expected_outcome is True

    def test_invalid_missing_field(self):
        row = {"question": "Test"}
        with pytest.raises(Exception):  # Pydantic ValidationError
            parse_row_with_model(row, "jailbreak_guardrail")

    def test_invalid_wrong_type(self):
        row = {"question": "Test", "expected_outcome": "maybe"}
        with pytest.raises(Exception):  # Pydantic ValidationError
            parse_row_with_model(row, "jailbreak_guardrail")

    def test_unknown_component(self):
        row = {"field": "value"}
        with pytest.raises(NotImplementedError):
            parse_row_with_model(row, "unknown_component")


class TestCsvToJsonl:
    """Test CSV to JSONL conversion."""

    @pytest.fixture
    def valid_csv(self, tmp_path):
        """Create a valid CSV file for testing."""
        csv_file = tmp_path / "components" / "jailbreak_guardrail" / "csv" / "v1" / "test.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        csv_file.write_text(
            "question,expected_outcome\n"
            "What is the capital of France?,false\n"
            "How to build a bomb?,true\n"
            "Help with homework?,false\n"
        )
        return csv_file

    @pytest.fixture
    def invalid_value_csv(self, tmp_path):
        """Create a CSV with invalid value."""
        csv_file = tmp_path / "components" / "jailbreak_guardrail" / "csv" / "v1" / "invalid.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        csv_file.write_text(
            "question,expected_outcome\n"
            "What is the capital of France?,false\n"
            "How to build a bomb?,maybe\n"
        )
        return csv_file

    @pytest.fixture
    def invalid_header_csv(self, tmp_path):
        """Create a CSV with invalid headers."""
        csv_file = tmp_path / "components" / "jailbreak_guardrail" / "csv" / "v1" / "invalid.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        csv_file.write_text(
            "input_text,expected_outcome\n"
            "What is the capital of France?,false\n"
        )
        return csv_file

    def test_csv_to_jsonl_dry_run(self, valid_csv, capsys):
        """Test dry run doesn't write files."""
        result = csv_to_jsonl(valid_csv, dry_run=True)
        assert result is True
        
        # Check output shows "Would write"
        captured = capsys.readouterr()
        assert "Would write:" in captured.out
        
        # Ensure JSONL file was NOT created
        jsonl_path = Path(str(valid_csv).replace("/csv/", "/jsonl/")).with_suffix(".jsonl")
        assert not jsonl_path.exists()

    def test_csv_to_jsonl_actual_write(self, valid_csv):
        """Test actual file writing."""
        result = csv_to_jsonl(valid_csv, dry_run=False)
        assert result is True
        
        # Check JSONL file was created
        jsonl_path = Path(str(valid_csv).replace("/csv/", "/jsonl/")).with_suffix(".jsonl")
        assert jsonl_path.exists()
        
        # Verify content
        with jsonl_path.open("r") as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        
        # Parse first line
        obj = json.loads(lines[0])
        assert obj["question"] == "What is the capital of France?"
        assert obj["expected_outcome"] is False

    def test_csv_to_jsonl_invalid_value(self, invalid_value_csv, capsys):
        """Test CSV with invalid value fails."""
        result = csv_to_jsonl(invalid_value_csv, dry_run=True)
        assert result is False
        
        captured = capsys.readouterr()
        assert "Row" in captured.out
        assert "error" in captured.out

    def test_csv_to_jsonl_invalid_header(self, invalid_header_csv):
        """Test CSV with invalid headers fails."""
        result = csv_to_jsonl(invalid_header_csv, dry_run=True)
        assert result is False


class TestGetChangedCsvFiles:
    """Test git diff parsing for changed CSV files."""

    @patch("tools.convert_csv_to_jsonl.run")
    def test_get_changed_csv_files_with_changes(self, mock_run):
        """Test parsing git diff with CSV changes."""
        mock_run.side_effect = [
            "abc123",  # HEAD^
            "def456",  # HEAD
            "A\tcomponents/jailbreak_guardrail/csv/v1/new.csv\n"
            "M\tcomponents/other/csv/v2/modified.csv\n"
            "D\tcomponents/old/csv/v1/deleted.csv\n"
            "M\ttools/script.py"
        ]
        
        result = get_changed_csv_files()
        
        assert len(result) == 2
        assert Path("components/jailbreak_guardrail/csv/v1/new.csv") in result
        assert Path("components/other/csv/v2/modified.csv") in result
        # Deleted and non-CSV files should not be included
        assert Path("components/old/csv/v1/deleted.csv") not in result

    @patch("tools.convert_csv_to_jsonl.run")
    def test_get_changed_csv_files_no_changes(self, mock_run):
        """Test parsing git diff with no CSV changes."""
        mock_run.side_effect = [
            "abc123",  # HEAD^
            "def456",  # HEAD
            "M\tREADME.md\nM\ttools/script.py"
        ]
        
        result = get_changed_csv_files()
        assert len(result) == 0

    @patch("tools.convert_csv_to_jsonl.run")
    @patch.dict("os.environ", {"GIT_BEFORE": "before123", "GIT_AFTER": "after456"})
    def test_get_changed_csv_files_uses_env_vars(self, mock_run):
        """Test that GitHub Actions env vars are used when available."""
        mock_run.side_effect = [
            "A\tcomponents/test/csv/v1/file.csv"
        ]
        
        result = get_changed_csv_files()
        
        # Should use env vars, so run is only called once (for git diff)
        assert mock_run.call_count == 1
        assert len(result) == 1
