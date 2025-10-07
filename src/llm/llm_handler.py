from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import SecretStr

# Load environment variables
load_dotenv()


class LLMHandler:
    def __init__(self):
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        secret_key: Optional[SecretStr] = SecretStr(api_key) if api_key else None
        self.llm = ChatOpenAI(temperature=0.0, api_key=secret_key.get_secret_value() if secret_key else None)

    def get_rag_prompt(self) -> PromptTemplate:
        template = """Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        Question: {question}
        Answer: """

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

    def get_llm(self) -> ChatOpenAI:
        return self.llm
