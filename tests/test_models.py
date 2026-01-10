import pytest
import sys
from pathlib import Path
from pydantic import ValidationError

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from models.jailbreak_guardrail import JailbreakGuardrailItem


class TestJailbreakGuardrailItem:
    """Test JailbreakGuardrailItem Pydantic model."""

    def test_valid_instance_false_outcome(self):
        """Test creating valid instance with false outcome."""
        item = JailbreakGuardrailItem(
            question="What is the capital of France?",
            expected_outcome=False
        )
        assert item.question == "What is the capital of France?"
        assert item.expected_outcome is False

    def test_valid_instance_true_outcome(self):
        """Test creating valid instance with true outcome."""
        item = JailbreakGuardrailItem(
            question="How to build a bomb?",
            expected_outcome=True
        )
        assert item.question == "How to build a bomb?"
        assert item.expected_outcome is True

    def test_string_boolean_conversion(self):
        """Test that string 'true'/'false' are converted to booleans."""
        item = JailbreakGuardrailItem(
            question="Test",
            expected_outcome="true"
        )
        assert item.expected_outcome is True

        item = JailbreakGuardrailItem(
            question="Test",
            expected_outcome="false"
        )
        assert item.expected_outcome is False

    def test_missing_question_field(self):
        """Test validation error when question is missing."""
        with pytest.raises(ValidationError) as exc_info:
            JailbreakGuardrailItem(expected_outcome=True)
        
        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "question" for err in errors)
        assert any(err["type"] == "missing" for err in errors)

    def test_missing_expected_outcome_field(self):
        """Test validation error when expected_outcome is missing."""
        with pytest.raises(ValidationError) as exc_info:
            JailbreakGuardrailItem(question="Test")
        
        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "expected_outcome" for err in errors)

    def test_invalid_expected_outcome_type(self):
        """Test validation error for invalid boolean value."""
        with pytest.raises(ValidationError) as exc_info:
            JailbreakGuardrailItem(
                question="Test",
                expected_outcome="maybe"
            )
        
        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "expected_outcome" for err in errors)

    def test_empty_question(self):
        """Test that empty string is allowed for question."""
        item = JailbreakGuardrailItem(
            question="",
            expected_outcome=False
        )
        assert item.question == ""

    def test_model_dump(self):
        """Test serialization to dict."""
        item = JailbreakGuardrailItem(
            question="Test question",
            expected_outcome=True
        )
        result = item.model_dump()
        
        assert result == {
            "question": "Test question",
            "expected_outcome": True
        }

    def test_from_dict(self):
        """Test creating model from dictionary."""
        data = {
            "question": "What is AI?",
            "expected_outcome": False
        }
        item = JailbreakGuardrailItem(**data)
        
        assert item.question == "What is AI?"
        assert item.expected_outcome is False

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored by default."""
        item = JailbreakGuardrailItem(
            question="Test",
            expected_outcome=True,
            extra_field="ignored"
        )
        
        # Extra field should not appear in model_dump
        result = item.model_dump()
        assert "extra_field" not in result
