from __future__ import annotations
import os
from typing import List
from backend.schemas.training_preparation_schema import ObjectiveRequest, KeyConceptRequest, ChecklistRequest, \
    ConceptOutput
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_objectives(request: ObjectiveRequest) -> List[str]:
    """
    Generate a list of training objectives for HR professionals based on the given request.

    Args:
        request (ObjectiveRequest): The request containing training details.

    Returns:
        List[str]: The generated list of objectives.
    """
    prompt = build_objective_prompt(request)
    response = call_llm(prompt)
    return parse_text_list(response, request.num_objectives)


def generate_key_concept(request: KeyConceptRequest) -> ConceptOutput:
    """
    Build a prompt based on the given KeyConceptRequest, call the LLM to generate a key concept,
    and parse the result into a ConceptOutput object.

    Args:
        request (KeyConceptRequest): The request object containing training details.

    Returns:
        ConceptOutput: The parsed key concept output object.

    Raises:
        ValueError: If the LLM response cannot be parsed as JSON.
    """
    prompt = build_key_concept_prompt(request)
    response = call_llm(prompt)

    try:
        parsed = json.loads(response)
        return ConceptOutput(**parsed)
    except Exception as e:
        raise ValueError(f"Could not parse JSON: {e}\nRaw output:\n{response}")


def generate_checklist(request: ChecklistRequest) -> List[str]:
    """
    Generate a preparation checklist for HR training.

    Args:
        request (ChecklistRequest): The request containing training details.

    Returns:
        List[str]: The generated checklist items.
    """
    prompt = build_checklist_prompt(request)
    response = call_llm(prompt)
    return parse_text_list(response, request.num_checkpoints)


def build_objective_prompt(request: ObjectiveRequest) -> str:
    """
    Build a prompt for the LLM to generate a preparation objective for HR training.

    Args:
        request (ObjectiveRequest): The request containing training details.

    Returns:
        str: The formatted prompt string.
    """
    return f"""You're a HR professionals training expert. Based on the case below, generate {request.num_objectives} clear, specific training objectives.

Category: {request.category}
Goal: {request.goal}
Context: {request.context}
Other Party: {request.other_party}

List:
1."""


def build_key_concept_prompt(request: KeyConceptRequest) -> str:
    """
    Build a prompt for the LLM to generate a preparation concept for HR training.

    Args:
        request (KeyConceptRequest): The request containing training details.

    Returns:
        str: The formatted prompt string.
    """
    return f"""
You are a training assistant. Based on the HR professionals training case below, generate **one** key concept and return it in the following strict JSON format.

Structure:
{{
  "header": "Title of the concept",
  "situation": "Describe the situation for this concept",
  "behavior": "Describe the recommended behavior",
  "impacts": "Describe the impact of applying this behavior",
  "text": [
    {{ "title": "Subpoint title", "body": "Explanation for the subpoint" }},
    {{ "title": "Another title", "body": "Explanation..." }}
  ]
}}


Only return a single JSON object. Do not include any explanations, formatting, or markdown.

Training Case:
- Category: {request.category}
- Goal: {request.goal}
- Context: {request.context}
- Other Party: {request.other_party}
"""


def build_checklist_prompt(request: ChecklistRequest) -> str:
    """
    Build a prompt for the LLM to generate a preparation checklist for HR training.

    Args:
        request (ChecklistRequest): The request containing training details.

    Returns:
        str: The formatted prompt string.
    """
    return f"""You're preparing for a HR professionals training session. Based on the following information, list {request.num_checkpoints} concrete preparation checklist items.

Category: {request.category}
Goal: {request.goal}
Context: {request.context}
Other Party: {request.other_party}

Checklist:
1."""


def call_llm(prompt: str) -> str:
    """
    Calls the OpenAI LLM with the given prompt and returns the response content as a string.

    Args:
        prompt (str): The prompt to send to the language model.

    Returns:
        str: The content of the model's response.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


def parse_text_list(text: str, max_items: int | None = None) -> List[str]:
    """
    Parse a multi-line string into a list of strings, removing leading numbering, dashes, or asterisks.

    Args:
        text (str): The input multi-line text, where each line may start with a number, dash, or asterisk.
        max_items (int | None): Maximum number of items to return. If None, return all items.

    Returns:
        List[str]: The processed list of items.
    """
    lines = text.splitlines()
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove leading "1. ", "- ", "* " etc.
        if line[0].isdigit() and "." in line:
            line = line.split(".", 1)[-1].strip()
        elif line.startswith(("-", "*")):
            line = line[1:].strip()
        items.append(line)
        if max_items and len(items) >= max_items:
            break
    return items
