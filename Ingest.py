import os

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter

from DocumentAnalyzer import DocumentAnalyzer
from helper import singleton
from Model import Model


@singleton
class VectorDB:
    index_name = None
    embeddings = None
    analyzer = None
    vector_store: AzureSearch

    def __init__(self):
        self.analyzer = DocumentAnalyzer()
        self.index_name = os.getenv("VECTORDB_INDEX_NAME")
        self.embeddings = Model().embeddings
        self.vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("VECTOR_STORE_ADDRESS"),
            azure_search_key=os.getenv("VECTOR_STORE_API_KEY"),
            index_name=self.index_name,
            embedding_function=self.embeddings,
        )

    def ingest(self, BlobId):
        documents = self.analyzer.analyze_blob(BlobId, "kb")
        text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
        docs = text_splitter.split_documents(
            [Document(page_content=documents, metadate={"tags": "kb"})]
        )
        print(self.vector_store.add_documents(docs))

    def query(self, content):
        data = self.vector_store.similarity_search(
            query=content, k=3, search_type="similarity"
        )
        print(data)
        return data
