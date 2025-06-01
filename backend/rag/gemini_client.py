# TODO: Connect with gemini connection later
import os

import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_gemini_llm(model_name: str = 'gemini-2.0-flash') -> ChatGoogleGenerativeAI:
    """
    Returns a LangChain-compatible Gemini LLM using the given model name.
    Requires GEMINI_API_KEY in the environment.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEY must be set in environment or .env file.')

    genai.configure(api_key=api_key)

    return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
