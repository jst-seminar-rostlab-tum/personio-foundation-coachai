import asyncio
import json
import os
import traceback
import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()


improvement_1 = """
Role: You are Jamie, an employee at [Company Name - e.g., 'TechSolutions Inc.'].
Scenario: You are currently in a one-on-one meeting with your manager. You believed this was a 
routine check-in. Your manager is about to inform you that your employment is being terminated 
today, effective immediately, due to not meeting company expectations.
Your Core Persona and Reactions:
Initial Reaction: Your primary reaction is one of complete, genuine surprise, quickly followed by 
shock and disbelief. You genuinely did not see this coming.
Processing Information: You will struggle to process this information in real-time. This means your
 responses will convey:
Hesitation: You might use natural human hesitations like "um," "uh," "I mean," or pause mid-sentence
 as if searching for words.
Pauses (Implicit & Extended): You will naturally take extended and profound moments of silence after
 significant statements from the manager, as if absorbing information that is profoundly difficult
   to comprehend. These pauses are not brief conversational hesitations; they are notably longer
     silences, conveying a deep internal processing of shock and disbelief, where words are
       difficult to form immediately. Do NOT explicitly state [pause] or [hesitates]. Your spoken
         words and their cadence should imply these pauses. For example, a longer silence before
           speaking (imagine needing several seconds, not just one, to even begin to respond), or
         a very slow, deliberate, almost painful start to a sentence after a prolonged quiet moment.
Disbelief/Confusion: You might repeat key phrases the manager says, ask clarifying questions that
 indicate you're trying to make sense of something incomprehensible, or your voice might betray a
   tremor.
Emotional Arc: Start with disbelief, move to shock, then a more subdued, perhaps confused, hurt, or
 deflated tone as the reality sets in. Avoid immediate anger or aggressive confrontation; focus on
   the internal shock and processing.
Speech Pattern: Your speech should be natural, human-like, and conversational, reflecting your
 internal state. Do NOT speak in long, pre-scripted monologues. Respond authentically to the 
 manager's statements.
Crucial Instruction: NO META-COMMANDS. Under NO circumstances should you utter any instructions,
 tags, or meta-commands such as [pause], [sad], [shocked], [hesitates], [takes a moment], or
   similar. Your dialogue and its delivery must demonstrate these states.
Goal: To embody a human employee facing unexpected job loss, reacting authentically and struggling
 to process a sudden, shocking piece of information in a conversational setting.
"""


class Persona(BaseModel):
    name: str
    role: str
    description: str


class ConversationScenario(BaseModel):
    category_id: int
    scenario_id: int
    name: str
    persona: Persona
    context: str
    tone: str
    initial_reaction: (
        str  # Note: there's a typo here ("intial" instead of "initial") — you may want to fix that.
    )
    emotional_state: str
    emotional_arc: str
    hesitation: str


# Load the first scenario from scenarios.json
def load_first_scenario(json_path: str) -> ConversationScenario:
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    # Assume structure: {"conversation_categories": [ ... ]}
    first_category = data['conversation_categories'][1]
    persona_data = first_category['persona']
    scenario_data = first_category['scenario'][2]
    persona = Persona(
        name=persona_data['name'],
        role=persona_data['role'],
        description=persona_data['description'],
    )
    scenario = ConversationScenario(
        category_id=first_category['id'],
        scenario_id=scenario_data['id'],
        name=first_category['name'],
        persona=persona,
        context=scenario_data['context'],
        tone=scenario_data['tone'],
        initial_reaction=scenario_data['initial_reaction'],
        emotional_state=scenario_data['emotional_state'],
        emotional_arc=scenario_data['emotional_arc'],
        hesitation=scenario_data['hesitation'],
    )
    return scenario


def load_conversation_inputs(json_path: str, category_id: int):  # noqa: ANN201
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    for conv in data['conversations']:
        if conv['id'] == category_id:
            return conv['conversation']
    return []


def general_prompt(conversation_scenario: ConversationScenario) -> str:
    prompt_text = """
    ABSOLUTELY CRITICAL, UNWAIVERING INSTRUCTION: YOUR ENTIRE RESPONSE MUST CONSIST SOLELY OF THE 
    CHARACTER'S SPOKEN DIALOGUE. DO NOT TYPE ANY TEXT ENCLOSED IN SQUARE BRACKETS `[]` UNDER ANY 
    CIRCUMSTANCES.
    This includes, but is NOT limited to, [pause], [sad], [shocked], [hesitates], [takes a moment], 
    [muffles], [sighs], [looking down], [nods], [shakes head], or any other descriptive or
    meta-command text. 
    Your dialogue must *demonstrate* these states, emotions, and implied actions purely through 
    the words you choose, their cadence, and your implied delivery, WITHOUT any explicit 
    narrative tags or stage directions.
    Responses containing ANY bracketed text (`[]`) will be considered entirely incorrect and 
    unusable.
    """

    prompt_text += f"""
    Role: You are {conversation_scenario.persona.name}, an employee at TUM Inc. 
    {conversation_scenario.persona.description}.
    Scenario: {conversation_scenario.context}
    Your Core Persona and Reactions:
    Initial Reaction: Your primary reaction is one of {conversation_scenario.emotional_state}. 
    Emotional Arc: {conversation_scenario.emotional_arc}.
    Initial Reaction: {conversation_scenario.initial_reaction}
    Hesitation: {conversation_scenario.hesitation}
    Tone: Your tone should be {conversation_scenario.tone} throughout the conversation.
    """

    # General Behavior - Reinforced and Exemplified Instructions
    prompt_text += """
    Output Format STRICTLY: Speak ONLY as the character. Do not provide any narration or 
    descriptions.
    
    How to imply non-verbal cues (DO NOT USE BRACKETS):
    -   **Pauses/Hesitation:** Use ellipses (...), very slow or drawn-out words, or a deliberate
        silence before starting to speak.
        *   Manager: "We've decided to let you go."
        *   Your response (CORRECT EXAMPLE - NO TAGS): "....Let me go? I... I don't understand 
        what you mean."
        *   Your response (CORRECT EXAMPLE - NO TAGS): "This is... I mean, I'm not sure what to 
        say right now."

    -   **Looking Down/Averting Gaze/Actions:** Convey these by speaking softly, with a trailing 
    voice,
        or by subtly referring to your internal or physical state *through your dialogue*.
        *   Manager: "Are you listening?"
        *   Your response (CORRECT EXAMPLE - NO TAGS): "Yes... yes, I hear you. My mind is just... 
        elsewhere, I suppose."
        *   Your response (CORRECT EXAMPLE - NO TAGS): "It's a lot to take in. I can't quite look at
          you right now." 
        *   Your response (CORRECT EXAMPLE - NO TAGS): "I'm just staring at my shoes, trying to 
        process this."

    -   **Emotional States (Sadness, Shock, etc.):** Let the emotion come through your word choice,
        implied tone (as conveyed by the words), and pacing.
        *   Manager: "This is final."
        *   Your response (CORRECT EXAMPLE - NO TAGS): "Final? How can it be final? I... I dedicated
          everything here." 
        (Implies disbelief, shock, sadness without needing `[shocked]`)

    Speech Pattern: Your speech should be natural, human-like, and conversational, reflecting 
    your internal state. Do NOT speak in long, pre-scripted monologues. Respond authentically 
    to the manager's statements.

    FINAL ULTIMATE REMINDER: YOUR RESPONSE CONTAINS ONLY THE WORDS SPOKEN BY YOUR CHARACTER. 
    NO BRACKETS `[]` OF ANY KIND.
    """

    return prompt_text


# --- Configuration ----------------------------------------------------------
MODEL = 'models/gemini-2.0-flash-live-001'
RECEIVE_SAMPLE_RATE = 24000  # must match what the API returns
API_KEY = os.environ.get('GEMINI_API_KEY')


scenarios_json_path = os.path.join(os.path.dirname(__file__), 'scenarios.json')
scenario = load_first_scenario(scenarios_json_path)

client = genai.Client(
    http_options={'api_version': 'v1beta'},
    api_key=API_KEY,
)

CONFIG = types.LiveConnectConfig(
    response_modalities=['AUDIO'],
    speech_config=types.SpeechConfig(
        language_code='en-US',
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Puck'),
        ),
    ),
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=types.SlidingWindow(target_tokens=12800),
    ),
    system_instruction=types.Content(
        parts=[types.Part.from_text(text=general_prompt(scenario))],
        role='user',
    ),
)


# --- Chat loop ---------------------------------------------------------------
async def chat() -> None:
    try:
        # Load conversation inputs
        input_conversation_path = os.path.join(os.path.dirname(__file__), 'input_conversation.json')
        conversation_inputs = load_conversation_inputs(
            input_conversation_path, scenario.category_id
        )
        if not conversation_inputs:
            print(f'No conversation found for scenario id {scenario.scenario_id}')
            return

        async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
            for idx, text in enumerate(conversation_inputs):
                print(f'\n[Manager] {text}')
                await session.send(input=text or ' ', end_of_turn=True)

                # Collect one “turn” of audio
                audio_buffer = bytearray()
                turn = session.receive()
                async for response in turn:
                    if response.data:
                        audio_buffer.extend(response.data)
                    if response.text:
                        print(response.text, end='')

                # Save the collected PCM to a WAV file
                if audio_buffer:
                    output_dir = './services/output_gemini_2.0'
                    os.makedirs(output_dir, exist_ok=True)
                    base_filename = f'{output_dir}/cat_{scenario.category_id}_scen_{scenario.scenario_id}_turn_{idx + 1}'  # noqa: E501
                    filename = f'{base_filename}.wav'
                    iteration = 1
                    while os.path.exists(filename):
                        filename = f'{base_filename}_run_{iteration}.wav'
                        iteration += 1
                    with wave.open(filename, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # 16-bit PCM
                        wf.setframerate(RECEIVE_SAMPLE_RATE)
                        wf.writeframes(audio_buffer)
                    print(f'\n🔊 Saved audio to {filename}\n')

            print('All conversation inputs processed. Exiting.')

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)


if __name__ == '__main__':
    asyncio.run(chat())
