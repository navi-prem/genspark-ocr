import unittest

import dotenv

from DocumentAnalyzer import DocumentAnalyzer
import helper


class TestAnalyzer(unittest.TestCase):
    def testFunc(self):
        dotenv.load_dotenv()
        uploader = helper.BlobUploader()
        key=""
        with open("./uploads/test.json","r") as f:
            data=f.read()
            key=uploader.upload_json(data)
            print(key)

        buffer = uploader.getBlobJsonData(key)

        data=buffer.decode('utf-8')

if __name__ == "__main__":
    unittest.main()
