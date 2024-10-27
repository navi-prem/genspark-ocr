import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential


class ImageAnalyzer:
    def get_env(self):
        try:
            endpoint = os.environ["VISION_ENDPOINT"]
            key = os.environ["VISION_KEY"]
            return endpoint,key
        except KeyError:
            raise Exception("Env Variables Not Found!")

    def __init__(self):
        self.endpoint,self.key= self.get_env()
        self.client = ImageAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )

    def analyze_image(self,image_path):
        if(not image_path or image_path==""):
            raise Exception("Image path is required!")

        visual_features =[
                VisualFeatures.TAGS,
                VisualFeatures.OBJECTS,
                VisualFeatures.CAPTION,
                VisualFeatures.DENSE_CAPTIONS,
                VisualFeatures.READ,
                VisualFeatures.SMART_CROPS,
                VisualFeatures.PEOPLE,
            ]
        #raising a request to azure for ocr
        with open(image_path, 'rb') as image:
            image_data=image.read()
            result = self.client.analyze (
                    image_data,
                    visual_features=visual_features,
                    gender_neutral_caption=True,
                    language="en",
                    smart_crops_aspect_ratios=[0.9, 1.33]
            )

        print("Result:")
        print(" Caption:")
        if result.caption is not None:
            print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")

        # Print text (OCR) analysis results to the console
        print(" Read:")
        if result.read is not None:
            for line in result.read.blocks[0].lines:
                print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
                for word in line.words:
                    print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")


