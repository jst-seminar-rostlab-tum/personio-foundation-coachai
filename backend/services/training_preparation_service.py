from __future__ import annotations

from backend.connections.openai_client import call_structured_llm
from backend.schemas.training_preparation_schema import (
    ChecklistRequest,
    KeyConceptOutput,
    KeyConceptRequest,
    ObjectiveRequest,
    StringListResponse,
)


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


def build_key_concept_prompt(request: KeyConceptRequest) -> str:
    return f"""
You are a training assistant. Based on the HR professionals training case below, 
generate 3-4 key concepts for the conversation.

Return them in a markdown format with the following structure:
- Each concept begins with a heading: ### Title
- Followed by a short descriptive paragraph
- Follow the exact formatting style shown in the example below (use `###`, `**`, etc.)
- Do not return any introductory text or explanations, just the markdown content
- Also include blank lines between sections for readability

Example format:

### The SBI Framework
- **Situation:** Describe the specific situation  
- **Behavior:** Address the specific behaviors observed  
- **Impact:** Explain the impact of those behaviors

### Active Listening
Show genuine interest in understanding the other person's perspective. 
Paraphrase what you've heard to confirm understanding.

### Use \"I\" Statements
Frame feedback in terms of your observations and feelings rather than accusations. 
For example, \"I noticed...\" instead of \"You always...\"

### Collaborative Problem-Solving
Work together to identify solutions rather than dictating next steps. 
Ask questions like \"What do you think would help in this situation?\"

---

Training Case:
- Category: {request.category}
- Goal: {request.goal}
- Context: {request.context}
- Other Party: {request.other_party}
"""


def generate_key_concept(request: KeyConceptRequest) -> str:
    prompt = build_key_concept_prompt(request)
    result = call_structured_llm(
        request_prompt=prompt,
        model='gpt-4o-2024-08-06',
        output_model=KeyConceptOutput,
    )
    return result.markdown
