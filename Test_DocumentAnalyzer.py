import unittest 
from DocumentAnalyzer import DocumentAnalyzer 
from dotenv import load_dotenv

class TestDocumentAnalyzer(unittest.TestCase):
    def test_docs(self):
        load_dotenv()
        analyzer=DocumentAnalyzer()
        analyzer.analyze_document("./uploads/test.pdf")


if __name__=="__main__":
    unittest.main()
