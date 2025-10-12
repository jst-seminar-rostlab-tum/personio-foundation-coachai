from __future__ import annotations

import concurrent.futures
import json
import os
from collections.abc import Callable, Generator
from contextlib import suppress
from functools import lru_cache
from uuid import UUID

from sqlmodel import Session as DBSession
from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.vertexai_client import call_structured_llm
from app.enums.language import LANGUAGE_NAME, LanguageCode
from app.enums.scenario_preparation_status import ScenarioPreparationStatus
from app.models.scenario_preparation import ScenarioPreparation
from app.schemas.scenario_prep_config import ScenarioPrepConfigRead
from app.schemas.scenario_preparation import (
    ChecklistCreate,
    KeyConcept,
    KeyConceptsCreate,
    KeyConceptsRead,
    ObjectivesCreate,
    ScenarioPreparationCreate,
    StringListRead,
)
from app.services.vector_db_context_service import get_hr_docs_context


@lru_cache
def load_scenario_prep_config() -> ScenarioPrepConfigRead:
    config_path = os.path.join(os.path.dirname(__file__), 'scenario_prep_config.json')
    with open(config_path, encoding='utf-8') as f:
        data = json.load(f)  # Python dict
    return ScenarioPrepConfigRead.model_validate(data)


CONFIG_PATH = os.path.join('app', 'config', 'scenario_prep_config.json')
config = load_scenario_prep_config()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_objectives(request: ObjectivesCreate, hr_docs_context: str = '') -> list[str]:
    return generate_objectives(request, hr_docs_context)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_checklist(request: ChecklistCreate, hr_docs_context: str = '') -> list[str]:
    return generate_checklist(request, hr_docs_context)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_key_concepts(
    request: KeyConceptsCreate, hr_docs_context: str = ''
) -> list[KeyConcept]:
    return generate_key_concept(request, hr_docs_context)


def generate_objectives(request: ObjectivesCreate, hr_docs_context: str = '') -> list[str]:
    """
    Generate a list of training objectives using structured output from the LLM.
    """

    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.objectives
    system_prompt = settings.system_prompts.objectives

    example_items = '\n'.join(mock_response.items)

    lang_name = LANGUAGE_NAME.get(lang, 'English')
    user_prompt = (
        f'Please write the following response in {lang_name}.\n\n'
        f'Generate {request.num_objectives} clear, specific training objectives based on '
        f'the following case:\n'
        f'Each item should be a single, concise sentence,'
        f' similar in length and style to the examples below.\n'
        f'Return the result strictly as a JSON object like:\n'
        f'{{ "items": ["Objective 1", "Objective 2", "Objective 3"] }}\n'
        f'Do not include markdown or ```json formatting.\n\n'
        f"Simply include the content and ignore 'Objective:'\n"
        f'Category: {request.category}\n'
        f'Persona the user is talking to including the training focus the user is focussing on '
        f'when talking to that persona: {request.persona}\n'
        f'Situational Facts: {request.situational_facts}\n'
        f'HR Document Context:\n'
        f'{hr_docs_context}'
        f'Here are example objectives items(for style and length reference only):\n'
        f'{example_items}'
    )

    result = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        output_model=StringListRead,
        mock_response=mock_response,
    )
    return result.items


def generate_checklist(request: ChecklistCreate, hr_docs_context: str = '') -> list[str]:
    """
    Generate a preparation checklist using structured output from the LLM.
    """
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.checklist
    system_prompt = settings.system_prompts.checklist

    example_items = '\n'.join(mock_response.items)

    lang_name = LANGUAGE_NAME.get(lang, 'English')
    user_prompt = (
        f'Please write the following response in {lang_name}.\n\n'
        f'Generate {request.num_checkpoints} checklist items for'
        f' the following conversation scenario:\n'
        f'Each item should be a single, concise sentence,'
        f' similar in length and style to the examples below.\n'
        f'Return the result strictly as a JSON object like:\n'
        f'{{ "items": ["Objective 1", "Objective 2", "Objective 3"] }}\n'
        f'Do not include markdown or ```json formatting.\n\n'
        f"Simply include the content and ignore 'Objective:'\n"
        f'Category: {request.category}\n'
        f'Persona (other party) incl. Training Focus: {request.persona}\n'
        f'Situational Facts: {request.situational_facts}\n'
        f'HR Document Context:\n'
        f'{hr_docs_context}'
        f'Here are example checklist items(for style and length reference only):\n'
        f'{example_items}'
    )
    result = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        output_model=StringListRead,
        mock_response=mock_response,
    )
    return result.items


def build_key_concept_prompt(
    request: KeyConceptsCreate,
    example: str,
    hr_docs_context: str = '',
    language_name: str = 'English',
) -> str:
    return f"""
Please write the following response in {language_name}.\n\n
Based on the HR professionals conversation scenario below, 
generate 3-4 key concepts for the conversation.

Your output must strictly follow this JSON format representing 
a Pydantic model `KeyConceptsRead`:

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

HR Document Context:
{hr_docs_context}

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
- Persona (other party) incl. Training Focus: {request.persona}
- Situational Facts: {request.situational_facts}
"""


def generate_key_concept(request: KeyConceptsCreate, hr_docs_context: str = '') -> list[KeyConcept]:
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.key_concepts
    system_prompt = settings.system_prompts.key_concepts

    lang_name = LANGUAGE_NAME.get(lang, 'English')
    prompt = build_key_concept_prompt(
        request, mock_response.model_dump_json(indent=4), hr_docs_context, lang_name
    )

    result = call_structured_llm(
        request_prompt=prompt,
        system_prompt=system_prompt,
        output_model=KeyConceptsRead,
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

    try:
        db_session = next(session_gen)
        # 1. retrieve the preparation record
        preparation = db_session.get(ScenarioPreparation, preparation_id)

        if not preparation:
            raise ValueError(f'Scenario preparation with ID {preparation_id} not found.')
        if preparation.status != ScenarioPreparationStatus.pending:
            raise ValueError(f'Scenario preparation {preparation_id} is not in pending status.')

        # 2. build request objects
        objectives_request = ObjectivesCreate(
            category=new_preparation.category,
            persona=new_preparation.persona,
            situational_facts=new_preparation.situational_facts,
            num_objectives=new_preparation.num_objectives,
            language_code=new_preparation.language_code,
        )
        checklist_request = ChecklistCreate(
            category=new_preparation.category,
            persona=new_preparation.persona,
            situational_facts=new_preparation.situational_facts,
            num_checkpoints=new_preparation.num_checkpoints,
            language_code=new_preparation.language_code,
        )
        key_concept_request = KeyConceptsCreate(
            category=new_preparation.category,
            persona=new_preparation.persona,
            situational_facts=new_preparation.situational_facts,
            language_code=new_preparation.language_code,
        )

        # hr_docs_context is used for LLM prompt; doc_names is available for future use
        hr_docs_context, doc_names, metadata = get_hr_docs_context(
            persona=new_preparation.persona,
            situational_facts=new_preparation.situational_facts,
            category=new_preparation.category,
        )

        has_error = False
        preparation.document_names = metadata

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
        with suppress(StopIteration):
            next(session_gen)


if __name__ == '__main__':
    # Example usage
    objective_request = ObjectivesCreate(
        category='Performance Feedback',
        persona='**Name**: Andrew '
        '**Training Focus**: Giving constructive criticism '
        '**Company Positon**: Junior engineer',
        situational_facts='Quarterly review',
        num_objectives=3,
        language_code=LanguageCode.de,
    )
    objectives = generate_objectives(objective_request)
    print('Generated Objectives:', objectives)

    checklist_request = ChecklistCreate(
        category='Performance Review',
        persona='**Name**: Sarah '
        '**Training Focus**: Addressing underperformance '
        '**Company Position**: Backend engineer',
        situational_facts='1:1 review',
        num_checkpoints=3,
        language_code=LanguageCode.de,
    )
    checklist = generate_checklist(checklist_request)
    print('Generated Checklist:', checklist)

    key_concept_request = KeyConceptsCreate(
        category='Performance Feedback',
        persona='**Name**: Jenny'
        '**Training Focus**: Giving constructive criticism '
        '**Company Position**: Junior engineer',
        situational_facts='Quarterly review',
        language_code=LanguageCode.de,
    )
    key_concept = generate_key_concept(key_concept_request)
    print(key_concept)
