from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

from .db_retrival import format_docs, get_vector_db_retriever
from .gemini_client import get_gemini_llm

retriever = get_vector_db_retriever()
query = 'Situational context' + 'Speaking Description' + '(Optional) Conversation summary'

llm = get_gemini_llm('gemini-2.0-flash')

prompt = PromptTemplate.from_template(
    '''You are a concise assistant that gives an answer to a query based on the provided context.
    Context: {context}
    Query: {query}
    Answer:'''
)

rag_chain = (
    RunnableLambda(lambda x: {'context': format_docs(retriever.invoke(x['query'])), 'query': x['query']})
    | prompt
    | llm
)

result = rag_chain.invoke({'query': query})

print(result.content)
