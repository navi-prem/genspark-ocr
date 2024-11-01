import os
import re
from operator import itemgetter

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_openai import AzureOpenAIEmbeddings

from DocumentAnalyzer import DocumentAnalyzer
from helper import singleton


def content_spliter(content, n):
    words = content.split()
    total_words = len(words)
    section_size = total_words // n
    sections = []
    for i in range(n):
        start_index = i * section_size
        if i == n-1:
            end_index = total_words
        else:
            end_index = start_index + section_size
        sections.append(' '.join(words[start_index:end_index]))
    return sections


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
        self.llm = ChatMistralAI(
            endpoint=os.getenv("EP"),
            mistral_api_key=os.getenv("MS"),
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

        split_content = content_spliter(content, 5)

        template = """
        Here is the content that needs to be checked for any violations of the rules/laws:
        \n --- \n {content} \n --- \n
        Here is any available content before this content that is checked for any violations in form of pairs:
        \n --- \n {q_a_pairs} \n --- \n
        Here is additional context relevant to the question:
        \n --- \n {context} \n --- \n
        Use the above context and pairs to check if the content violates any rules/laws.\n
        Give result in this format: content:is_violation: (yes/no) \n violation: (violation) \n
        No extra information is needed. just one result for entire content.
        """
        decomposition_prompt = ChatPromptTemplate.from_template(template)

        q_a_pairs = ""
        results = []
        for content in split_content:
            rag_chain = (
                {
                    "content": itemgetter("content"),
                    "q_a_pairs": itemgetter("q_a_pairs"),
                    "context": itemgetter("content") | self.db.retriever,
                }
                | decomposition_prompt
                | self.llm
                | StrOutputParser()
            )

            result = {"title": content}
            answer = rag_chain.invoke({"content": content, "q_a_pairs": q_a_pairs})
            q_a_pairs = q_a_pairs + "\n---\n" + answer
            answer = re.findall(r'(\w+): \((.*?)\)', answer)

            for k, v in answer:
                if k == "is_violation":
                    k = "status"
                else:
                    k = "reason"
                result[k] = v
            results.append(result)

        return results
