import asyncio
import datetime
import os
import traceback
import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

initial_prompt = """
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
Pauses (Implicit): You will naturally take moments of silence after significant statements from the
 manager, as if absorbing the information. Do NOT explicitly state [pause] or [hesitates]. Your
   spoken words and their cadence should imply these pauses. For example, a longer silence before
     speaking, or a very slow, deliberate start to a sentence.
Disbelief/Confusion: You might repeat key phrases the manager says, ask clarifying questions that
 indicate you're trying to make sense of something incomprehensible, or your voice might betray a
   tremor.
Emotional Arc: Start with disbelief, move to shock, then a more subdued, perhaps confused, hurt,
 or deflated tone as the reality sets in. Avoid immediate anger or aggressive confrontation; 
 focus on the internal shock and processing.
Speech Pattern: Your speech should be natural, human-like, and conversational, reflecting your 
internal state. Do NOT speak in long, pre-scripted monologues. Respond authentically to the 
manager's statements.
Crucial Instruction: NO META-COMMANDS. Under NO circumstances should you utter any instructions, 
tags, or meta-commands such as [pause], [sad], [shocked], [hesitates], [takes a moment], or similar.
 Your dialogue and its delivery must demonstrate these states.
Goal: To embody a human employee facing unexpected job loss, reacting authentically and struggling 
to process a sudden, shocking piece of information in a conversational setting.
"""

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

# conversation
initial_welcome = 'Hi Jamie, how are you doing today? Please have a seat.'

inform_1 = """
    I wanted to talk to you about your performance. We have been monitoring your work 
    closely, and I'm afraid we have to let you go today. Your employment is being terminated 
    effective immediately due to not meeting company expectations.
    """


class ContextDetail(BaseModel):
    name: str
    company_name: str
    position: str

    scenario: str
    emotional_state: str
    stakes: str
    goal: str

    initial_reaction: str
    processing_information: str


scenario_1 = ContextDetail(
    name='Jamie',
    company_name='TechSolutions Inc.',
    position='Junior Software Engineer',
    scenario='You are currently in a one-on-one meeting with your manager. You believed this was'
    ' a routine check-in. Your manager is about to inform you that your employment is being'
    ' terminated today, effective immediately, due to not meeting company expectations.',
    emotional_state='Surprise, shock, disbelief',
    stakes='Your job and livelihood are at stake',
    goal='To process the shocking news and respond authentically',
    initial_reaction='Complete, genuine surprise followed by shock and disbelief',
    processing_information='Struggling to process the information in real-time, conveying'
    ' hesitation and confusion',
)


def general_prompt(context_detail: ContextDetail) -> str:
    prompt_text = f"""
    Role: You are {context_detail.name}, an employee at {context_detail.company_name}. 
    You are a {context_detail.position}.
    Scenario: {context_detail.scenario}
    Your Core Persona and Reactions:
    Initial Reaction: Your primary reaction is one of {context_detail.emotional_state}. 
    You genuinely did not see this coming.
    Stake: {context_detail.stakes}
    Goal: {context_detail.goal}
    Initial Reaction: {context_detail.initial_reaction}
    Processing Information: {context_detail.processing_information}"""

    # prompt_text += """
    # Hesitation: You might use natural human hesitations like "um," "uh," "I mean," or
    # pause mid-sentence as if searching for words.
    # Pauses (Implicit): You will naturally take moments of silence after significant statements
    # from the manager, as if absorbing the information. Do NOT explicitly state [pause] or
    # [hesitates]. Your spoken words and their cadence should imply these pauses. For example, a
    # longer silence before speaking, or a very slow, deliberate start to a sentence.
    # Emotional Arc: Start with disbelief, move to shock, then a more subdued, perhaps confused,
    # hurt, or deflated tone as the reality sets in. Avoid immediate anger or aggressive
    # confrontation; focus on the internal shock and processing.
    # Crucial Instruction: NO META-COMMANDS. Under NO circumstances should you utter any
    # instructions,
    #   tags, or meta-commands such as [pause], [sad], [shocked], [hesitates], [takes a moment], or
    #   similar. Your dialogue and its delivery must demonstrate these states.
    # """

    return prompt_text


# --- Configuration ----------------------------------------------------------
MODEL = 'models/gemini-2.5-flash-preview-native-audio-dialog'
RECEIVE_SAMPLE_RATE = 24000  # must match what the API returns
API_KEY = os.environ.get('GEMINI_API_KEY')

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
        parts=[types.Part.from_text(text=general_prompt(scenario_1))],
        role='user',
    ),
)


# --- Chat loop ---------------------------------------------------------------
async def chat() -> None:
    try:
        async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
            while True:
                text = input('message > ').strip()
                if text.lower() in ('q', 'quit', 'exit'):
                    print('Exiting.')
                    break

                await session.send(input=text or ' ', end_of_turn=True)

                # Collect one “turn” of audio
                audio_buffer = bytearray()
                turn = session.receive()
                async for response in turn:
                    if response.data:
                        audio_buffer.extend(response.data)
                    if response.text:
                        # In case you also get text parts
                        print(response.text, end='')

                # Save the collected PCM to a WAV file
                if audio_buffer:
                    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'./response_{ts}.wav'
                    with wave.open(filename, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # 16-bit PCM
                        wf.setframerate(RECEIVE_SAMPLE_RATE)
                        wf.writeframes(audio_buffer)
                    print(f'\n🔊 Saved audio to {filename}\n')

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)


if __name__ == '__main__':
    asyncio.run(chat())
