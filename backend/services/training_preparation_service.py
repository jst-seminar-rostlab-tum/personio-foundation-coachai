from __future__ import annotations
import os
from typing import List
from backend.schemas.traning_preparation_schema import ObjectiveRequest, KeyConceptRequest, ChecklistRequest, \
    ConceptOutput
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_objectives(request: ObjectiveRequest) -> List[str]:
    prompt = build_objective_prompt(request)
    response = call_llm(prompt)
    return parse_text_list(response, request.num_objectives)


def generate_key_concept(request: KeyConceptRequest) -> ConceptOutput:
    prompt = build_key_concept_prompt(request)
    response = call_llm(prompt)

    try:
        parsed = json.loads(response)
        return ConceptOutput(**parsed)
    except Exception as e:
        raise ValueError(f"Could not parse JSON: {e}\nRaw output:\n{response}")


def generate_checklist(request: ChecklistRequest) -> List[str]:
    prompt = build_checklist_prompt(request)
    response = call_llm(prompt)
    return parse_text_list(response, request.num_checkpoints)


def build_objective_prompt(request: ObjectiveRequest) -> str:
    return f"""You're a HR professionals training expert. Based on the case below, generate {request.num_objectives} clear, specific training objectives.

Category: {request.category}
Goal: {request.goal}
Context: {request.context}
Other Party: {request.other_party}

List:
1."""


def build_key_concept_prompt(request: KeyConceptRequest) -> str:
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
    return f"""You're preparing for a HR professionals training session. Based on the following information, list {request.num_checkpoints} concrete preparation checklist items.

Category: {request.category}
Goal: {request.goal}
Context: {request.context}
Other Party: {request.other_party}

Checklist:
1."""


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


def parse_text_list(text: str, max_items: int | None = None) -> List[str]:
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


if __name__ == "__main__":
    from backend.schemas.traning_preparation_schema import ObjectiveRequest, KeyConceptRequest, ChecklistRequest

    req = KeyConceptRequest(category="Performance Management",
                            goal="Give constructive feedback to a low-performing employee",
                            context="1-on-1 feedback session after a poor quarterly review",
                            other_party="Software Engineer")
    print(generate_key_concept(req))
