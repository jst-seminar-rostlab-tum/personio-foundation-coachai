from unittest.mock import MagicMock, patch

from app.schemas.scenario_preparation import (
    ChecklistRequest,
    KeyConcept,
    KeyConceptRequest,
    KeyConceptResponse,
    ObjectiveRequest,
    StringListResponse,
)
from app.services.scenario_preparation_service import (
    generate_checklist,
    generate_key_concept,
    generate_objectives,
)


@patch('app.services.scenario_preparation_service.call_structured_llm')
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


@patch('app.services.scenario_preparation_service.call_structured_llm')
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


@patch('app.services.scenario_preparation_service.call_structured_llm')
def test_generate_key_concept_parses_json(mock_llm: MagicMock) -> None:
    mock_key_concept_response = [
        KeyConcept(
            header='Clear Communication',
            value='Express ideas clearly and listen actively to understand others.',
        ),
        KeyConcept(
            header='Empathy', value="Show understanding and concern for the other party's feelings."
        ),
        KeyConcept(
            header='Effective Questioning',
            value='Ask open-ended questions to encourage dialogue and exploration.',
        ),
    ]

    mock_llm.return_value = KeyConceptResponse(items=mock_key_concept_response)

    req = KeyConceptRequest(
        category='Feedback',
        goal='Deliver effective criticism',
        context='Post-project debrief',
        other_party='Project manager',
    )

    result = generate_key_concept(req)
    assert all(isinstance(x, KeyConcept) for x in result)
    assert result == mock_key_concept_response
