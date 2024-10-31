from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from helper import singleton


@singleton
class Model:
    llm = None
    embeddings = None
    __system_msg = (
        "system",
        "you are a helpfull assistant that checks wheather the given content obeys the rules/laws or not with the help of context",
    )

    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment="tuskact1",
            api_version="2024-05-01-preview",
            temperature=0.1,
            max_tokens=100,
            timeout=10,
            max_retries=0,
        )

        self.embeddings = AzureOpenAIEmbeddings(
            model="tuskact2",
        )

    def query(self, content):
        responce = self.llm.invoke([self.__system_msg, content])
        return responce

    def rag(self):
        pass
