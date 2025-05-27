from unittest.mock import MagicMock, patch

from backend.schemas.training_preparation_schema import (
    ChecklistRequest,
    KeyConceptOutput,
    KeyConceptRequest,
    ObjectiveRequest,
    StringListResponse,
)
from backend.services.training_preparation_service import (
    generate_checklist,
    generate_key_concept,
    generate_objectives,
)


@patch('backend.services.training_preparation_service.call_structured_llm')
def test_generate_objectives_returns_correct_list(mock_llm: MagicMock) -> None:
    items = ['1. Prepare outline', '2. Rehearse responses', '3. Stay calm']
    mock_llm.return_value = StringListResponse(items=items)

    req = ObjectiveRequest(
        category='Performance Feedback',
        goal='Give constructive criticism',
        context='Quarterly review',
        other_party='Junior engineer',
        num_objectives=3,
    )

    result = generate_objectives(req)
    assert len(result) == 3
    assert all(isinstance(item, str) for item in result)
    for i in range(len(result)):
        assert result[i] == items[i]


@patch('backend.services.training_preparation_service.call_structured_llm')
def test_generate_checklist_returns_correct_list(mock_llm: MagicMock) -> None:
    items = ['1. Review past performance', '2. Prepare documents', '3. Set up private room']
    mock_llm.return_value = StringListResponse(items=items)

    req = ChecklistRequest(
        category='Performance Review',
        goal='Address underperformance',
        context='1:1 review',
        other_party='Backend engineer',
        num_checkpoints=3,
    )

    result = generate_checklist(req)
    assert len(result) == 3
    for i in range(len(result)):
        assert result[i] == items[i]


@patch('backend.services.training_preparation_service.call_structured_llm')
def test_generate_key_concept_parses_json(mock_llm: MagicMock) -> None:
    markdown_output = """
   ### The SBI Framework
- **Situation:** Describe the specific situation  
- **Behavior:** Address the specific behaviors observed  
- **Impact:** Explain the impact of those behaviors  

### Active Listening
Show genuine interest in understanding the other person's perspective. 
Paraphrase what you've heard to confirm understanding.

### Use "I" Statements
Frame feedback in terms of your observations and feelings rather than accusations. 
For example, "I noticed..." instead of "You always..."

### Collaborative Problem-Solving
Work together to identify solutions rather than dictating next steps. 
Ask questions like "What do you think would help in this situation?"

    """
    mock_llm.return_value = KeyConceptOutput(markdown=markdown_output)

    req = KeyConceptRequest(
        category='Feedback',
        goal='Deliver effective criticism',
        context='Post-project debrief',
        other_party='Project manager',
    )

    result = generate_key_concept(req)
    assert isinstance(result, str)
    assert result == markdown_output
