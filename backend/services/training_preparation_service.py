from __future__ import annotations

from collections.abc import Callable, Generator
from uuid import UUID

from backend.connections.openai_client import call_structured_llm
from backend.models import TrainingPreparation, TrainingPreparationStatus
from backend.schemas.training_preparation_schema import (
    ChecklistRequest,
    KeyConcept,
    KeyConceptOutput,
    KeyConceptRequest,
    ObjectiveRequest,
    StringListResponse,
    TrainingPreparationRequest,
)
from sqlmodel import Session


def generate_objectives(request: ObjectiveRequest) -> list[str]:
    """
    Generate a list of training objectives using structured output from the LLM.
    """
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
        f'Here are example objectives items(for style and length reference only):\n'
        f'Clearly communicate the impact of the missed deadlines\n'
        f'Understand potential underlying causes\n'
        f'Collaboratively develop a solution\n'
        f'End the conversation on a positive note'
    )

    result = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt='You are a training expert generating learning objectives.',
        model='gpt-4o-2024-08-06',
        output_model=StringListResponse,
    )
    return result.items


def generate_checklist(request: ChecklistRequest) -> list[str]:
    """
    Generate a preparation checklist using structured output from the LLM.
    """
    user_prompt = (
        f'Generate {request.num_checkpoints} checklist items for the following training case:\n'
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
        f'Here are example checklist items(for style and length reference only):\n'
        f'Gather specific examples of missed deadlines\n'
        f'Document the impact on team and projects\n'
        f'Consider potential underlying causes\n'
        f'Prepare open-ended questions\n'
        f'Think about potential solutions to suggest\n'
        f'Plan a positive closing statement\n'
        f'Choose a private, comfortable meeting environment\n'
    )

    result = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt='You are a training expert generating preparation checklists.',
        model='gpt-4o-2024-08-06',
        output_model=StringListResponse,
    )
    return result.items


def build_key_concept_prompt(
    request: KeyConceptRequest,
) -> str:
    return f"""
You are a training assistant. Based on the HR professionals training case below, 
generate 3-4 key concepts for the conversation.

Your output must strictly follow this JSON format representing a Pydantic model `KeyConceptOutput`:

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

Instructions:
- Do not include any text outside of the JSON structure.
- Use exactly the field names: 'items', 'header', 'value'.
- Extract up to 4 key concepts.
- Each key concept must have a 'header' as a short title, and a 'value' as description.
- Use proper JSON syntax, including double quotes.
- Do not return any explanations, introductions, or markdown syntax.
- Include blank lines for readability if you want, but only inside JSON string values.

Example output:

{{
  "items": [
    {{
      "header": "The SBI Framework",
      "value": "Situation: Describe the specific situation. Behavior: Address the specific \n
      behaviors observed. Impact: Explain the impact of those behaviors."
    }},
    {{
      "header": "Active Listening",
      "value": "Show genuine interest in understanding the other person's perspective.\n
       Paraphrase what you've heard to confirm understanding."
    }}
    {{
      "header": "Constructive Feedback",
      "value": "Provide feedback that is specific, actionable, and focused on behaviors \n
      rather than personal attributes."
    }},
    {{
      "header": "Positive Closure",
      "value": "End the conversation on a positive note, reinforcing the relationship \n
      and future collaboration."
    }}
  ]
}}

---

Training Case:
- Category: {request.category}
- Goal: {request.goal}
- Context: {request.context}
- Other Party: {request.other_party}
"""


def generate_key_concept(request: KeyConceptRequest) -> list[KeyConcept]:
    prompt = build_key_concept_prompt(request)
    result = call_structured_llm(
        request_prompt=prompt,
        model='gpt-4o-2024-08-06',
        output_model=KeyConceptOutput,
    )
    return result.items


def create_pending_preparation(case_id: UUID, session: Session) -> TrainingPreparation:
    """
    Create a new TrainingPreparation record with status 'pending'.
    """
    prep = TrainingPreparation(
        case_id=case_id,
        status=TrainingPreparationStatus.pending,
        objectives=[],
        key_concepts=[],
        prep_checklist=[],
    )
    session.add(prep)
    session.commit()
    return prep


def generate_training_preparation(
    preparation_id: UUID,
    request: TrainingPreparationRequest,
    session_generator_func: Callable[[], Generator[Session, None, None]],
    # Function to generate a new session
) -> TrainingPreparation:
    """
    Generate training preparation data including objectives, checklist, and key concepts.
    Updates the TrainingPreparation record and returns it.
    """

    # Ensure the session generator is called to get a new session
    session_gen = session_generator_func()
    session = next(session_gen)

    try:
        # 1. retrieve the preparation record
        preparation = session.get(TrainingPreparation, preparation_id)

        if not preparation:
            raise ValueError(f'Training preparation with ID {preparation_id} not found.')
        if preparation.status != TrainingPreparationStatus.pending:
            raise ValueError(f'Training preparation {preparation_id} is not in pending status.')

        try:
            # 2. generate objectives, checklist, and key concepts
            objectives_request = ObjectiveRequest(
                category=request.category,
                goal=request.goal,
                context=request.context,
                other_party=request.other_party,
                num_objectives=request.num_objectives,
            )
            checklist_request = ChecklistRequest(
                category=request.category,
                goal=request.goal,
                context=request.context,
                other_party=request.other_party,
                num_checkpoints=request.num_checkpoints,
            )
            key_concept_request = KeyConceptRequest(
                category=request.category,
                goal=request.goal,
                context=request.context,
                other_party=request.other_party,
            )

            # 3. Generate the content using the LLM
            objectives = generate_objectives(objectives_request)
            checklist = generate_checklist(checklist_request)
            key_concepts = generate_key_concept(key_concept_request)

            # 4. update the preparation record
            preparation.objectives = objectives
            preparation.prep_checklist = checklist
            preparation.key_concepts = [ex.dict() for ex in key_concepts]
            preparation.status = TrainingPreparationStatus.completed

        except Exception:
            # 4. handle any errors during generation
            preparation.status = TrainingPreparationStatus.failed

        session.add(preparation)
        session.commit()
        session.refresh(preparation)
        return preparation

    finally:
        # 5. ensure the session is closed properly
        try:
            session_gen.close()
        except Exception as e:
            print(f'[WARN] Failed to close session generator: {e}')
