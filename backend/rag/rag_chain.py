from langchain.prompts import PromptTemplate

from .gemini_client import get_gemini_llm

llm = get_gemini_llm('gemini-2.0-flash')

prompt = PromptTemplate.from_template('Summarize the topic: {topic}')

chain = prompt | llm

result = chain.invoke({'topic': 'conflict resolution'})

print(result.content)
