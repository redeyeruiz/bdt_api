import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from pprint import pprint
from io import BytesIO
from PIL import Image, ImageDraw
from random import random
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials


class Sentinel:
    def init_face(self):
        self.__KEY = "2d304d0279b940c9a1ec082568ae0827"
        self.__ENDPOINT = "https://bdt-faceanalyzer.cognitiveservices.azure.com/"
        self.__CLIENT = FaceClient(self.__ENDPOINT, CognitiveServicesCredentials(self.__KEY))

    def init_text(self):
        self.__KEY = "b1b396b5527847c696f42e0cf7a9099d"
        self.__ENDPOINT = "https://bdt-textanalyzer.cognitiveservices.azure.com/"
        self.__CLIENT = FaceClient(self.__ENDPOINT, CognitiveServicesCredentials(self.__KEY))

    def init_image(self):
        self.__KEY = "b35f3e3f9e1743b2bb56f81f768f20ad"
        self.__ENDPOINT = "https://bdt-mediaanalyzer.cognitiveservices.azure.com/"
        self.__CLIENT = ComputerVisionClient(endpoint=self.__ENDPOINT,credentials=CognitiveServicesCredentials(self.__KEY))
    
    def analyze_image(self, image_url):
        remote_image_features = ["adult"]
        print("\nEvaluate for adult and racy and gory content.")
        # Call API with URL and features
        results = self.__CLIENT.analyze_image(image_url, remote_image_features)

        # Print results with adult/racy score
        print("Analyzing remote image for adult or racy or gory content ... ")
        #print("Is adult content: {} with confidence {:.2f}".format(detect_adult_results_remote.adult.is_adult_content, detect_adult_results_remote.adult.adult_score * 100))
        #print("Has racy content: {} with confidence {:.2f}".format(detect_adult_results_remote.adult.is_racy_content, detect_adult_results_remote.adult.racy_score * 100))

        if results.adult.is_adult_content or results.adult.is_racy_content or results.adult.is_gory_content:
            return True
        else:
            return False

    def analyze_text(self, text):
        text_list = []
        text_list.append(text)
        ta_credential = AzureKeyCredential(self.__KEY)
        self.__CLIENT = TextAnalyticsClient(endpoint=self.__ENDPOINT, credential=ta_credential)

        response = self.__CLIENT.analyze_sentiment(documents=text_list)[0]
        #print("Document Sentiment: {}".format(response.sentiment))

        # print("Overall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(
        #     response.confidence_scores.positive,
        #     response.confidence_scores.neutral,
        #     response.confidence_scores.negative,
        # ))
        return response.sentiment

    def verify_faces(self, image1_url, image2_url):
        # Detect face(s) from source image 1, returns a list[DetectedFaces]
        # We use detection model 3 to get better performance.7
        try: # Throws exception if no faces found

            detected_face1 = self.__CLIENT.face.detect_with_url(image1_url, detection_model='detection_03')
            image1_id = detected_face1[0].face_id

            detected_face2 = self.__CLIENT.face.detect_with_url(image2_url, detection_model='detection_03')
            image2_id = detected_face2[0].face_id
        
            # Verification example for faces of the same person. The higher the confidence, the more identical the faces in the images are.
            # Since target faces are the same person, in this example, we can use the 1st ID in the detected_faces_ids list to compare.
            verify_result_same = self.__CLIENT.face.verify_face_to_face(image1_id, image2_id)

            if verify_result_same.is_identical:
                #print('Faces are of the same person, with confidence:', verify_result_same.confidence)
                return True
            else: 
                #print('Faces are of a different person, with confidence:', verify_result_same.confidence)
                return False
        except Exception:
            return False # We took it as a negative
        

# s = Sentinel()
# s.init_face()

# url = "https://filesmanager070901.blob.core.windows.net/imagenes/Cara/"

# imagen1_id = "PERFIL-704a6e57-e7f1-43b0-b63d-53a7fbbab0a91632838273979.jpg"
# imagen2_id = "PLANO-c4d5ddf4-f3b4-4ce8-9eb1-b9421f66e5541632838415522.jpg"
# imagen3_id = "WOW-64f6f959-16ed-406a-8e2e-ca68f7fc6d931632838426136.jpg"
# imagen4_id = "EYE-c0cf6bbc-41ae-45da-9498-fb650c325c5a1632838433495.jpg"

# result1 = s.verify_faces(url+imagen1_id, url+imagen2_id)
# result2 = s.verify_faces(url+imagen2_id, url+imagen3_id)
# result3 = s.verify_faces(url+imagen3_id, url+imagen4_id)


# print(result1, result2, result3)

# print(s.verify_faces("https://filesmanager070901.blob.core.windows.net/imagenes/Cara/e5b35390-352e-404b-a935-5cf9b549e99c.jpeg", "https://filesmanager070901.blob.core.windows.net/imagenes/Cara/sho.jpg"))

# s = Sentinel()
# s.init_text()
# print(s.analyze_text("me parece que es un buen album"))


# s = Sentinel()
# s.init_image()
# print(s.analyze_image("https://filesmanager070901.blob.core.windows.net/tests/polla.jpeg"))

