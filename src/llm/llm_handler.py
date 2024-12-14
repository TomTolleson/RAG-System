from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from src.config.settings import OPENAI_API_KEY, TEMPERATURE

class LLMHandler:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
    
    def get_rag_prompt(self):
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        Question: {question}
        Answer: """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def get_llm(self):
        return self.llm
