from __future__ import annotations

from typing import TypeVar

from backend.connections.openai_client import get_client
from backend.schemas.training_preparation_schema import (
    ChecklistRequest,
    KeyConceptOutput,
    KeyConceptRequest,
    ObjectiveRequest,
    StringListResponse,
)
from pydantic import BaseModel

client = get_client()
# This is a type variable for the output model, which must be a subclass of BaseModel
T = TypeVar("T", bound=BaseModel)


def call_structured_llm(
        request_prompt: str,
        system_prompt: str,
        model: str,
        output_model: type[T],
        temperature: float = 1,
        max_tokens: int = 500
) -> BaseModel:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return output_model.model_validate_json(response.choices[0].message.content.strip())


def generate_objectives(request: ObjectiveRequest) -> list[str]:
    """
    Generate a list of training objectives using structured output from the LLM.
    """
    user_prompt = (
        f"Generate {request.num_objectives} clear, specific training objectives based on "
        f"the following case:\n"
        f"Return the result strictly as a JSON object like:\n"
        f'{{ "items": ["Objective 1", "Objective 2", "Objective 3"] }}\n'
        f"Do not include markdown or ```json formatting.\n\n"
        f"Simply include the content and ignore 'Objective:'\n"
        f"Category: {request.category}\n"
        f"Goal: {request.goal}\n"
        f"Context: {request.context}\n"
        f"Other Party: {request.other_party}"
    )

    result = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt="You are a training expert generating learning objectives.",
        model="gpt-4o-2024-08-06",
        output_model=StringListResponse,
    )
    return result.items


def generate_checklist(request: ChecklistRequest) -> list[str]:
    """
    Generate a preparation checklist using structured output from the LLM.
    """
    user_prompt = (
        f"Generate {request.num_checkpoints} checklist items for the following training case:\n"
        f"Return the result strictly as a JSON object like:\n"
        f'{{ "items": ["Objective 1", "Objective 2", "Objective 3"] }}\n'
        f"Do not include markdown or ```json formatting.\n\n"
        f"Simply include the content and ignore 'Objective:'\n"
        f"Category: {request.category}\n"
        f"Goal: {request.goal}\n"
        f"Context: {request.context}\n"
        f"Other Party: {request.other_party}"
    )

    result = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt="You are a training expert generating preparation checklists.",
        model="gpt-4o-2024-08-06",
        output_model=StringListResponse,
    )
    return result.items


def generate_key_concept(request: KeyConceptRequest) -> KeyConceptOutput:
    prompt = build_key_concept_prompt(request)
    markdown = call_llm(prompt)
    return KeyConceptOutput(markdown=markdown)


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


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()
