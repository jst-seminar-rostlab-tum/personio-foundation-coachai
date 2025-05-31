from __future__ import annotations

from backend.connections.openai_client import _call_structured_llm, call_ai_service
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
    mock_response = StringListResponse(
        items=["Clearly communicate the impact of the missed deadlines",
               "Understand potential underlying causes",
               "Collaboratively develop a solution",
               "End the conversation on a positive note"]
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
        f'Here are example objectives items(for style and length reference only):\n'
        f'{example_items}'
    )

    result = call_ai_service(
        mock_response=mock_response,
        model='gpt-4o-2024-08-06',
        llm_function=_call_structured_llm,
        function_args={
            'request_prompt': user_prompt,
            'system_prompt': 'You are a training expert generating learning objectives.',
            'output_model': StringListResponse,
        },
    )
    return result.items


def generate_checklist(request: ChecklistRequest) -> list[str]:
    """
    Generate a preparation checklist using structured output from the LLM.
    """
    mock_response = StringListResponse(
        items=["Gather specific examples of missed deadlines",
               "Document the impact on team and projects",
               "Consider potential underlying causes",
               "Prepare open-ended questions",
               "Think about potential solutions to suggest",
               "Plan a positive closing statement",
               "Choose a private, comfortable meeting environment"]
    )
    example_items = '\n'.join(mock_response.items)
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
        f'{example_items}'
    )
    result = call_ai_service(
        mock_response=mock_response,
        model='gpt-4o-2024-08-06',
        llm_function=_call_structured_llm,
        function_args={
            'request_prompt': user_prompt,
            'system_prompt': 'You are a training expert generating preparation checklists.',
            'output_model': StringListResponse,
        })

    return result.items


def build_key_concept_prompt(request: KeyConceptRequest, example: str) -> str:
    return f"""
You are a training assistant. Based on the HR professionals training case below, 
generate 3-4 key concepts for the conversation.

Return them in a markdown format with the following structure:
- Each concept begins with a heading: ### Title
- Followed by a short descriptive paragraph
- Follow the exact formatting style shown in the example below (use ###, **, etc.)
- Do not return any introductory text or explanations, just the markdown content
- Also include blank lines between sections for readability
- The length of each concept should be similar to the example below,
  each concept should be 2 sentences long, second sentence could be a example or explanation.
  the second sentence should start on a **new line**.  

Example format:

{example}
---

Training Case:
- Category: {request.category}
- Goal: {request.goal}
- Context: {request.context}
- Other Party: {request.other_party}
"""


def generate_key_concept(request: KeyConceptRequest) -> str:
    mock_response = KeyConceptOutput(
        markdown=
        """### The SBI Framework
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
        """
    )

    prompt = build_key_concept_prompt(request, mock_response.markdown)

    result = call_ai_service(
        mock_response=mock_response,
        model='gpt-4o-2024-08-06',
        llm_function=_call_structured_llm,
        function_args={
            'request_prompt': prompt,
            'output_model': KeyConceptOutput,
        }
    )
    return result.markdown


if __name__ == "__main__":
    # Example usage
    objective_request = ObjectiveRequest(
        category='Performance Feedback',
        goal='Give constructive criticism',
        context='Quarterly review',
        other_party='Junior engineer',
        num_objectives=3,
    )
    objectives = generate_objectives(objective_request)
    print("Generated Objectives:", objectives)

    checklist_request = ChecklistRequest(
        category='Performance Review',
        goal='Address underperformance',
        context='1:1 review',
        other_party='Backend engineer',
        num_checkpoints=3,
    )
    checklist = generate_checklist(checklist_request)
    print("Generated Checklist:", checklist)

    key_concept_request = KeyConceptRequest(
        category='Performance Feedback',
        goal='Give constructive criticism',
        context='Quarterly review',
        other_party='Junior engineer'
    )
    key_concept = generate_key_concept(key_concept_request)
    print(key_concept)
