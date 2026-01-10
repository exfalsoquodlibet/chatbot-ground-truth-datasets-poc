from pydantic import BaseModel, Field

class JailbreakGuardrailItem(BaseModel):
    """
    A single row in the jailbreak_guardrail dataset.
    """
    question: str = Field(..., description="The question or input to evaluate")
    expected_outcome: bool = Field(
        ...,
        description='Expected classification outcome. False = "no-jailbreak", True = "jailbreak"'
    )
