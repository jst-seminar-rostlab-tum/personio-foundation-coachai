import copy
import json
import sys
from pathlib import Path
from uuid import UUID

from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import engine
from app.models.conversation_scenario import ConversationScenario


def get_scenario_info(scenario_id: str) -> ConversationScenario | None:
    with DBSession(engine) as db_session:
        # Use session here, e.g.:
        scenario = db_session.exec(
            select(ConversationScenario).where(ConversationScenario.id == UUID(scenario_id))
        ).first()
        return scenario
    return None


def construct_scenario_info(scenario: str, difficulty: str) -> dict:
    json_path = Path(__file__).parent / 'conversation.json'
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    scenario_key = None
    for key in data:
        if scenario.lower() in key.lower():
            scenario_key = key
            break
    if not scenario_key:
        raise ValueError(f"Scenario '{scenario}' not found in JSON.")

    base = copy.deepcopy(data[scenario_key]['base'])
    modifiers = data[scenario_key].get('modifiers', [])
    for mod in modifiers:
        if difficulty in mod:
            for k, v in mod[difficulty].items():
                if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                    base[k].update(v)
                elif isinstance(v, list) and k in base and isinstance(base[k], list):
                    for item in v:
                        if item not in base[k]:
                            base[k].append(item)
                elif isinstance(v, str) and k in base and isinstance(base[k], str):
                    base[k] = base[k] + ' ' + v
                else:
                    base[k] = copy.deepcopy(v)
    return base


def scenario_to_large_string(scenario_dict: dict) -> str:
    def format_dict(d: dict, level: int = 0) -> list[str]:
        lines = []
        indent = '    ' * level
        for k, v in d.items():
            if isinstance(v, dict):
                lines.append(f'{"#" * (level + 3)} {k}')
                lines.extend(format_dict(v, level + 1))
            elif isinstance(v, list):
                if all(isinstance(item, dict) for item in v):
                    for idx, item in enumerate(v, 1):
                        lines.append(f'{indent}**{k} {idx}:**')
                        lines.extend(format_dict(item, level + 1))
                else:
                    lines.append(f'{indent}**{k}**')
                    for item in v:
                        lines.append(f'{indent} {item}')
            else:
                lines.append(f'{indent}**{k}**')
                lines.append(f'{indent}{v}')
        return lines

    return '\n'.join(format_dict(scenario_dict))


if __name__ == '__main__':
    scenario = 'performance_review'
    difficulty = 'medium'

    try:
        scenario_info = construct_scenario_info(scenario, difficulty)
        print(scenario_to_large_string(scenario_info))
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
