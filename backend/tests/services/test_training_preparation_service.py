import pytest
from unittest.mock import patch
from backend.services.training_preparation_service import (
    generate_objectives, generate_key_concept, generate_checklist
)
from backend.schemas.training_preparation_schema import (
    ObjectiveRequest, KeyConceptRequest, ChecklistRequest, ConceptOutput
)

@patch("backend.services.training_preparation_service.call_llm")
def test_generate_objectives_returns_correct_list(mock_llm):
    mock_llm.return_value = "1. Prepare outline\n2. Rehearse responses\n3. Stay calm"

    req = ObjectiveRequest(
        category="Performance Feedback",
        goal="Give constructive criticism",
        context="Quarterly review",
        other_party="Junior engineer",
        num_objectives=3
    )

    result = generate_objectives(req)
    assert len(result) == 3
    assert all(isinstance(item, str) for item in result)
    assert result[0].startswith("Prepare")


@patch("backend.services.training_preparation_service.call_llm")
def test_generate_checklist_returns_correct_list(mock_llm):
    mock_llm.return_value = "1. Review past performance\n2. Prepare documents\n3. Set up private room"

    req = ChecklistRequest(
        category="Performance Review",
        goal="Address underperformance",
        context="1:1 review",
        other_party="Backend engineer",
        num_checkpoints=3
    )

    result = generate_checklist(req)
    assert len(result) == 3
    assert "Review" in result[0]


@patch("backend.services.training_preparation_service.call_llm")
def test_generate_key_concept_parses_json(mock_llm):
    mock_llm.return_value = """
    {
        "header": "SBI Framework",
        "situation": "Feedback on missed deadlines",
        "behavior": "Describe observable actions",
        "impacts": "Helps clarify consequences and reduce conflict",
        "text": [
            { "title": "Be Specific", "body": "Focus on actual events" },
            { "title": "Stay Neutral", "body": "Avoid judgment" }
        ]
    }
    """

    req = KeyConceptRequest(
        category="Feedback",
        goal="Deliver effective criticism",
        context="Post-project debrief",
        other_party="Project manager"
    )

    result = generate_key_concept(req)
    assert isinstance(result, ConceptOutput)
    assert result.header == "SBI Framework"
    assert len(result.text) == 2
    assert result.text[0].title == "Be Specific"


@patch("backend.services.training_preparation_service.call_llm")
def test_generate_key_concept_raises_on_bad_json(mock_llm):
    mock_llm.return_value = "This is not JSON"

    req = KeyConceptRequest(
        category="Feedback",
        goal="Test error case",
        context="Some context",
        other_party="Someone"
    )

    with pytest.raises(ValueError) as e:
        generate_key_concept(req)
    assert "Could not parse JSON" in str(e.value)