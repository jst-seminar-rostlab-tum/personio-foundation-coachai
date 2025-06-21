from __future__ import annotations

import concurrent.futures
from collections.abc import Callable, Generator
from uuid import UUID

from sqlmodel import Session as DBSession
from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.openai_client import call_structured_llm
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationStatus
from app.schemas.scenario_preparation import (
    ChecklistRequest,
    KeyConcept,
    KeyConceptRequest,
    KeyConceptResponse,
    ObjectiveRequest,
    ScenarioPreparationCreate,
    StringListResponse,
)
from app.services.vector_db_context_service import query_vector_db_and_prompt


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_objectives(
    request: ObjectiveRequest, vector_db_prompt_extension: str = ''
) -> list[str]:
    return generate_objectives(request, vector_db_prompt_extension)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_checklist(
    request: ChecklistRequest, vector_db_prompt_extension: str = ''
) -> list[str]:
    return generate_checklist(request, vector_db_prompt_extension)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_key_concepts(
    request: KeyConceptRequest, vector_db_prompt_extension: str = ''
) -> list[KeyConcept]:
    return generate_key_concept(request, vector_db_prompt_extension)


def generate_objectives(
    request: ObjectiveRequest, vector_db_prompt_extension: str = ''
) -> list[str]:
    """
    Generate a list of training objectives using structured output from the LLM.
    """
    mock_response = StringListResponse(
        items=[
            'Clearly communicate the impact of the missed deadlines',
            'Understand potential underlying causes',
            'Collaboratively develop a solution',
            'End the conversation on a positive note',
        ]
    )
    example_items = '\n'.join(mock_response.items)

    user_prompt = (
        f'Generate {request.num_objectives} clear, specific training objectives based on '
        f'the following case:\n'
        f'Each item should be a single, concise sentence,'
        f' similar in length and style to the examples below.\n'
        f'Return the result strictly as a JSON object like:\n'
        f'{{ "items": ["Objective 1", "Objective 2", "Objective 3"] }}\n'
        f'Do not include markdown or ```json formatting.\n\n'
        f"Simply include the content and ignore 'Objective:'\n"
        f'Category: {request.category}\n'
        f'Goal: {request.goal}\n'
        f'Context: {request.context}\n'
        f'Other Party: {request.other_party}'
        f'{vector_db_prompt_extension}'
        f'Here are example objectives items(for style and length reference only):\n'
        f'{example_items}'
    )

    result = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt='You are a training expert generating learning objectives.',
        model='gpt-4o-2024-08-06',
        output_model=StringListResponse,
        mock_response=mock_response,
    )
    return result.items


def generate_checklist(
    request: ChecklistRequest, vector_db_prompt_extension: str = ''
) -> list[str]:
    """
    Generate a preparation checklist using structured output from the LLM.
    """
    mock_response = StringListResponse(
        items=[
            'Gather specific examples of missed deadlines',
            'Document the impact on team and projects',
            'Consider potential underlying causes',
            'Prepare open-ended questions',
            'Think about potential solutions to suggest',
            'Plan a positive closing statement',
            'Choose a private, comfortable meeting environment',
        ]
    )
    example_items = '\n'.join(mock_response.items)

    user_prompt = (
        f'Generate {request.num_checkpoints} checklist items for'
        f' the following conversation scenario:\n'
        f'Each item should be a single, concise sentence,'
        f' similar in length and style to the examples below.\n'
        f'Return the result strictly as a JSON object like:\n'
        f'{{ "items": ["Objective 1", "Objective 2", "Objective 3"] }}\n'
        f'Do not include markdown or ```json formatting.\n\n'
        f"Simply include the content and ignore 'Objective:'\n"
        f'Category: {request.category}\n'
        f'Goal: {request.goal}\n'
        f'Context: {request.context}\n'
        f'Other Party: {request.other_party}'
        f'{vector_db_prompt_extension}'
        f'Here are example checklist items(for style and length reference only):\n'
        f'{example_items}'
    )
    result = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt='You are a training expert generating preparation checklists.',
        model='gpt-4o-2024-08-06',
        output_model=StringListResponse,
        mock_response=mock_response,
    )
    return result.items


def build_key_concept_prompt(
    request: KeyConceptRequest, example: str, vector_db_prompt_extension: str = ''
) -> str:
    return f"""
You are a training assistant. Based on the HR professionals conversation scenario below, 
generate 3-4 key concepts for the conversation.

Your output must strictly follow this JSON format representing 
a Pydantic model `KeyConceptResponse`:

{{
  "items": [
    {{
      "header": "Title of the key concept",
      "value": "A short descriptive paragraph about the concept"
    }},
    {{
      "header": "Another key concept",
      "value": "Description for this concept"
    }}
  ]
}}

{vector_db_prompt_extension}

Instructions:
- Do not include any text outside of the JSON structure.
- Use exactly the field names: 'items', 'header', 'value'.
- Extract up to 4 key concepts.
- Each key concept must have a 'header' as a short title, and a 'value' as description.
- Use proper JSON syntax, including double quotes.
- Do not return any explanations, introductions, or markdown syntax.
- Include blank lines for readability if you want, but only inside JSON string values.

Example output:

{example}
---

Conversation scenario:
- Category: {request.category}
- Goal: {request.goal}
- Context: {request.context}
- Other Party: {request.other_party}
"""


def generate_key_concept(
    request: KeyConceptRequest, vector_db_prompt_extension: str = ''
) -> list[KeyConcept]:
    mock_key_concept = [
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
    mock_response = KeyConceptResponse(items=mock_key_concept)

    prompt = build_key_concept_prompt(
        request, mock_response.model_dump_json(indent=4), vector_db_prompt_extension
    )

    result = call_structured_llm(
        request_prompt=prompt,
        model='gpt-4o-2024-08-06',
        output_model=KeyConceptResponse,
        mock_response=mock_response,
    )
    return result.items


def create_pending_preparation(scenario_id: UUID, db_session: DBSession) -> ScenarioPreparation:
    """
    Create a new ScenarioPreparation record with status 'pending'.
    """
    prep = ScenarioPreparation(
        scenario_id=scenario_id,
        status=ScenarioPreparationStatus.pending,
        objectives=[],
        key_concepts=[],
        prep_checklist=[],
    )
    db_session.add(prep)
    db_session.commit()
    return prep


def generate_scenario_preparation(
    preparation_id: UUID,
    new_preparation: ScenarioPreparationCreate,
    session_generator_func: Callable[[], Generator[DBSession, None, None]],
) -> ScenarioPreparation:
    """
    Generate scenario preparation data including objectives, checklist, and key concepts.
    Updates the ScenarioPreparation record and returns it.
    """

    session_gen = session_generator_func()
    db_session = next(session_gen)

    try:
        # 1. retrieve the preparation record
        preparation = db_session.get(ScenarioPreparation, preparation_id)

        if not preparation:
            raise ValueError(f'Scenario preparation with ID {preparation_id} not found.')
        if preparation.status != ScenarioPreparationStatus.pending:
            raise ValueError(f'Scenario preparation {preparation_id} is not in pending status.')

        # 2. build request objects
        objectives_request = ObjectiveRequest(
            category=new_preparation.category,
            goal=new_preparation.goal,
            context=new_preparation.context,
            other_party=new_preparation.other_party,
            num_objectives=new_preparation.num_objectives,
        )
        checklist_request = ChecklistRequest(
            category=new_preparation.category,
            goal=new_preparation.goal,
            context=new_preparation.context,
            other_party=new_preparation.other_party,
            num_checkpoints=new_preparation.num_checkpoints,
        )
        key_concept_request = KeyConceptRequest(
            category=new_preparation.category,
            goal=new_preparation.goal,
            context=new_preparation.context,
            other_party=new_preparation.other_party,
        )

        hr_docs_context = query_vector_db_and_prompt(
            session_context=[request.category, request.goal, request.context, request.other_party],
            generated_object='output',
        )

        has_error = False

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_key_concepts = executor.submit(
                safe_generate_key_concepts, key_concept_request, hr_docs_context
            )
            future_objectives = executor.submit(
                safe_generate_objectives, objectives_request, hr_docs_context
            )
            future_checklist = executor.submit(
                safe_generate_checklist, checklist_request, hr_docs_context
            )

            try:
                preparation.objectives = future_objectives.result()
            except Exception as e:
                has_error = True
                print('[ERROR] Failed to generate objectives:', e)

            try:
                preparation.prep_checklist = future_checklist.result()
            except Exception as e:
                has_error = True
                print('[ERROR] Failed to generate checklist:', e)

            try:
                key_concepts = future_key_concepts.result()
                preparation.key_concepts = [ex.model_dump() for ex in key_concepts]
            except Exception as e:
                has_error = True
                print('[ERROR] Failed to generate key concepts:', e)

        if has_error:
            preparation.status = ScenarioPreparationStatus.failed
        else:
            preparation.status = ScenarioPreparationStatus.completed

        db_session.add(preparation)
        db_session.commit()
        db_session.refresh(preparation)
        return preparation

    finally:
        try:
            session_gen.close()
        except Exception as e:
            print(f'[WARN] Failed to close session generator: {e}')


if __name__ == '__main__':
    # Example usage
    objective_request = ObjectiveRequest(
        category='Performance Feedback',
        goal='Give constructive criticism',
        context='Quarterly review',
        other_party='Junior engineer',
        num_objectives=3,
    )
    objectives = generate_objectives(objective_request)
    print('Generated Objectives:', objectives)

    checklist_request = ChecklistRequest(
        category='Performance Review',
        goal='Address underperformance',
        context='1:1 review',
        other_party='Backend engineer',
        num_checkpoints=3,
    )
    checklist = generate_checklist(checklist_request)
    print('Generated Checklist:', checklist)

    key_concept_request = KeyConceptRequest(
        category='Performance Feedback',
        goal='Give constructive criticism',
        context='Quarterly review',
        other_party='Junior engineer',
    )
    key_concept = generate_key_concept(key_concept_request)
    print(key_concept)
