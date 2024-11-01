import unittest

import dotenv

from DocumentAnalyzer import DocumentAnalyzer


class TestAnalyzer(unittest.TestCase):
    def testFunc(self):
        dotenv.load_dotenv()
        self.file_name = "test.pdf$04f9a945-c454-471c-b6b7-d4e165c03503"
        analyzer = DocumentAnalyzer()
        data=analyzer.analyze_blob(self.file_name, "kb")
        print(data)


if __name__ == "__main__":
    unittest.main()
