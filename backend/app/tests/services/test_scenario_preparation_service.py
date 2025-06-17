from unittest.mock import MagicMock, patch

from app.schemas.scenario_preparation_schema import (
    ChecklistRequest,
    KeyConcept,
    KeyConceptOutput,
    KeyConceptRequest,
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

    mock_llm.return_value = KeyConceptOutput(items=mock_key_concept_response)

    req = KeyConceptRequest(
        category='Feedback',
        goal='Deliver effective criticism',
        context='Post-project debrief',
        other_party='Project manager',
    )

    result = generate_key_concept(req)
    assert all(isinstance(x, KeyConcept) for x in result)
    assert result == mock_key_concept_response


@patch('app.services.scenario_preparation_service.call_structured_llm')
def test_generate_objectives_with_vector_db_prompt_extension(mock_llm: MagicMock) -> None:
    # Analogically for checklist and concepts

    # Set up llm mock and vector db prompt extension
    mock_llm.return_value = StringListResponse(items=['Objective 1', 'Objective 2'])

    req = ObjectiveRequest(
        category='Feedback',
        goal='Improve team dynamics',
        context='Team meeting',
        other_party='Team lead',
        num_objectives=2,
    )

    vector_db_prompt_extension_base = (
        'The output you generate should comply with the following HR Guideline excerpts:\n'
    )
    vector_db_prompt_extension_1 = f'{vector_db_prompt_extension_base}Respect\n2. Clarity\n'
    vector_db_prompt_extension_2 = ''

    # Assert for vector_db_prompt_extension_1
    _ = generate_objectives(req, vector_db_prompt_extension=vector_db_prompt_extension_1)
    assert mock_llm.called
    args, kwargs = mock_llm.call_args
    request_prompt = kwargs['request_prompt']
    assert vector_db_prompt_extension_1 in request_prompt

    # Assert for vector_db_prompt_extension_2
    _ = generate_objectives(req, vector_db_prompt_extension=vector_db_prompt_extension_2)
    assert mock_llm.called
    args, kwargs = mock_llm.call_args
    request_prompt = kwargs['request_prompt']
    assert vector_db_prompt_extension_base not in request_prompt
    assert len(request_prompt) > 0
