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

    base = data[scenario_key]['base'].copy()
    modifiers = data[scenario_key].get('modifiers', [])
    for mod in modifiers:
        if difficulty in mod:
            # Merge modifier into base
            for k, v in mod[difficulty].items():
                if isinstance(v, dict) and k in base:
                    base[k].update(v)
                elif isinstance(v, list) and k in base:
                    base[k].extend(v)
                else:
                    base[k] = v
    return base


def scenario_to_large_string(scenario_dict: dict) -> str:
    return json.dumps(scenario_dict, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    scenario = 'giving_feedback'
    difficulty = 'hard'

    try:
        scenario_info = construct_scenario_info(scenario, difficulty)
        print(scenario_to_large_string(scenario_info))
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
