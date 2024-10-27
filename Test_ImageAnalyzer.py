import unittest
from ImageAnalyzer import ImageAnalyzer
from dotenv import load_dotenv

class TestImageAnalyzer(unittest.TestCase):
    def test_image(self):
        load_dotenv()
        analyzer = ImageAnalyzer()
        analyzer.analyze_image("./uploads/test.jpg")

if __name__ =="__main__":
    unittest.main()

