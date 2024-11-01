# import libraries
import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (AnalyzeDocumentRequest,
                                                  AnalyzeResult)
from azure.core.credentials import AzureKeyCredential


class DocumentAnalyzer:
    def _get_words(self, page, line):
        result = []
        for word in page.words:
            if self._in_span(word, line.spans):
                result.append(word)
        return result

    def _in_span(self, word, spans):
        for span in spans:
            if word.span.offset >= span.offset and (
                word.span.offset + word.span.length
            ) <= (span.offset + span.length):
                return True
        return False

    def _get_env(self):
        try:
            self.key = os.environ["DOCUMENTAI_KEY"]
            self.endpoint = os.environ["DOCUMENTAI_ENDPOINT"]
            self.kb_container_name = os.environ["KB_CONTAINER_NAME"]
            self.rag_container_name = os.environ["RAG_CONTAINER_NAME"]
            self.storage_account = os.environ["STORAGE_ACCOUNT"]
        except KeyError:
            raise Exception("Env Variables Not Found!")

    def __init__(self):
        self._get_env()
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )

    def _get_blob_url(self, blob_key, container_name):
        blob_key = blob_key.strip()
        return f"https://{self.storage_account}.blob.core.windows.net/{container_name}/{blob_key}"

    def analyze_blob(self, blob_key: str, key: str):
        if blob_key == "":
            raise Exception("Blob Key Cannot be ''.")
        if key != "rag" and key != "kb":
            raise Exception("Choose key 'rag' or 'kb'.")

        # choose the  appropriate container
        container_name = (
            self.rag_container_name if key == "rag" else self.kb_container_name
        )

        poller = self.client.begin_analyze_document(
            "prebuilt-layout",
            AnalyzeDocumentRequest(
                url_source=self._get_blob_url(blob_key, container_name)
            ),
        )
        result: AnalyzeResult = poller.result()

        if result.styles and any([style.is_handwritten for style in result.styles]):
            print("Document contains handwritten content")
        else:
            print("Document does not contain handwritten content")

        # the code below gives the content of the document
        # use streaming as the content can be large
        content = ""
        for page in result.pages:
            if page.lines:
                for _, line in enumerate(page.lines):
                    # vector db
                    content += line.content + " "
        return content

    def analyze_document(self, file_path: str):
        if not file_path or file_path == "":
            raise Exception("Invalid file path")

        with open(file_path, "rb") as f:
            bytes_source = f.read()
            poller = self.client.begin_analyze_document(
                "prebuilt-layout", AnalyzeDocumentRequest(bytes_source=bytes_source)
            )

            result: AnalyzeResult = poller.result()

            if result.styles and any([style.is_handwritten for style in result.styles]):
                print("Document contains handwritten content")
            else:
                print("Document does not contain handwritten content")

            # the code below gives the content of the document
            # use streaming as the content can be large
            for page in result.pages:
                if page.lines:
                    for _, line in enumerate(page.lines):
                        # vector db
                        print(line.content)
