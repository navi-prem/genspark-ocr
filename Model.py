import os
from operator import itemgetter

from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.azureml_endpoint import (
    AzureMLEndpointApiType,
    AzureMLOnlineEndpoint,
    CustomOpenAIContentFormatter,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from DocumentAnalyzer import DocumentAnalyzer
from helper import singleton


def format_qa_pair(question, answer):
    """Format Q and A pair"""
    formatted_string = ""
    formatted_string += f"Question: {question}\nAnswer: {answer}\n\n"
    return formatted_string.strip()


@singleton
class Model:
    llm = None
    embeddings = None
    analyzer = None
    db = None
    __system_msg = (
        "system",
        "you are a helpfull assistant that checks wheather the given content obeys the rules/laws or not with the help of context",
    )

    def __init__(self):
        # self.llm = AzureChatOpenAI(
        #     azure_deployment="tuskact1",
        #     api_version="2024-05-01-preview",
        #     temperature=0.1,
        #     max_tokens=100,
        #     timeout=10,
        #     max_retries=0,
        # )
        self.llm = AzureMLOnlineEndpoint(
            endpoint_url=os.getenv("NEP"),
            endpoint_api_type=AzureMLEndpointApiType.serverless,
            endpoint_api_key=os.getenv("MS"),
            model_kwargs={"temperature": 0.2, "max_new_tokens": 200},
        )

        self.embeddings = AzureOpenAIEmbeddings(
            model="tuskact2",
        )

        self.analyzer = DocumentAnalyzer()

    def query(self, content):
        responce = self.llm.invoke([self.__system_msg, content])
        return responce

    def rag(self, blob_key):
        from Ingest import VectorDB

        self.db = VectorDB()

        content = self.analyzer.analyze_blob(blob_key, "rag")

        template = """
        you are a helpfull assistant that splits the given content into multiple parts
        such that it can be used for further processing.\n given content: {content} \n
        Output (3 queries):
        """
        content_decomposition = ChatPromptTemplate.from_template(template)
        generate = (
            content_decomposition
            | self.llm
            | StrOutputParser()
            | (lambda x: x.split("."))
        )
        split_content = generate.invoke({"content": content})

        template = """
        Here is the content that needs to be checked for any violations of the rules/laws:
        \n --- \n {content} \n --- \n
        Here is any available background question + answer pairs:
        \n --- \n {q_a_pairs} \n --- \n
        Here is additional context relevant to the question:
        \n --- \n {context} \n --- \n
        Use the above context and any background question + answer pairs to check if the content violates any rules/laws.
        """
        decomposition_prompt = ChatPromptTemplate.from_template(template)

        q_a_pairs = self.db.query("people")
        for content in split_content:
            rag_chain = (
                {
                    "content": itemgetter(content),
                    "q_a_pairs": itemgetter(q_a_pairs),
                    "context": itemgetter(content) | self.db.query(content),
                }
                | decomposition_prompt
                | self.llm
                | StrOutputParser()
            )
            answer = rag_chain.invoke({"content": content, "q_a_pairs": q_a_pairs})
            q_a_pairs += "\n---\n" + format_qa_pair(content, answer)

        print(q_a_pairs)
