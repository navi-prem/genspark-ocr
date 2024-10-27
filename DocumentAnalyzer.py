# import libraries
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

class DocumentAnalyzer():
    def get_words(self,page, line):
        result = []
        for word in page.words:
            if self._in_span(word, line.spans):
                result.append(word)
        return result

    def _in_span(self,word, spans):
        for span in spans:
            if word.span.offset >= span.offset and (
                word.span.offset + word.span.length
            ) <= (span.offset + span.length):
                return True
        return False
    def get_env(self):
        try:
            key= os.environ["DOCUMENTAI_KEY"]
            endpoint = os.environ["DOCUMENTAI_ENDPOINT"]
            return endpoint,key
        except KeyError:
            raise Exception("Env Variables Not Found!")

    def __init__(self):
        self.endpoint,self.key=self.get_env()
        self.client= DocumentIntelligenceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )

    def analyze_document(self,file_path:str):
        if(not file_path or file_path==""):
            raise Exception("Invalid file path")

        with open(file_path,'rb') as f:
            bytes_source=f.read()
            poller = self.client.begin_analyze_document(
                "prebuilt-layout", AnalyzeDocumentRequest(bytes_source=bytes_source
            ))

            result: AnalyzeResult = poller.result()

            if result.styles and any([style.is_handwritten for style in result.styles]):
                print("Document contains handwritten content")
            else:
                print("Document does not contain handwritten content")

            for page in result.pages:
                if page.lines:
                    for _, line in enumerate(page.lines):
                        # words = self.get_words(page, line)
                        print(line.content)
                        # print(
                        #     f"...Line # {line_idx} has word count {len(words)} and text '{line.content}' "
                        #     # f"within bounding polygon '{line.polygon}'"
                        # )
                        #
                        # for word in words:
                        #     print(
                        #         f"......Word '{word.content}' has a confidence of {word.confidence}"
                        #     )

                # if page.selection_marks:
                #     for selection_mark in page.selection_marks:
                #         print(
                #             f"Selection mark is '{selection_mark.state}' within bounding polygon "
                #             f"'{selection_mark.polygon}' and has a confidence of {selection_mark.confidence}"
                #         )

            # if result.tables:
            #     for table_idx, table in enumerate(result.tables):
            #         print(
            #             f"Table # {table_idx} has {table.row_count} rows and "
            #             f"{table.column_count} columns"
            #         )
            #         if table.bounding_regions:
            #             for region in table.bounding_regions:
            #                 print(
            #                     f"Table # {table_idx} location on page: {region.page_number} is {region.polygon}"
            #                 )
            #         for cell in table.cells:
            #             print(
            #                 f"...Cell[{cell.row_index}][{cell.column_index}] has text '{cell.content}'"
            #             )
            #             if cell.bounding_regions:
            #                 for region in cell.bounding_regions:
            #                     print(
            #                         f"...content on page {region.page_number} is within bounding polygon '{region.polygon}'"
            #                     )

            print("----------------------------------------")

