import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def get_client() -> OpenAI:
    """
    Returns the OpenAI client instance.

    returns:
    - OpenAI client instance
    """
    return client
