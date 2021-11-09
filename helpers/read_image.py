from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
import config as c


def read_img(img):
    """
    OCR operation: Read the image using the Read API
    create an instance of the computervisionclient using the credentials. call the read_in_stream method (because its a local image)
     providing the img and seeting reading order to natural
    The reading_order='natural' argument ensures that if KP's image is a two-sided, it is read as a human would
    operation_id is retrieved from the response header and used to get the read results.
    :param: image to read
    :return: a list of the text found in the image, separated by end of line
    """
    # print("Extracting text from image remotely...")

    # create an instance of the computer vision client
    client = ComputerVisionClient(c.azure_credentials['endpoint'],
                                                 CognitiveServicesCredentials(c.azure_credentials['key1']))
    # call API with the image url
    response = client.read_in_stream(img, reading_order='natural', raw=True)
    read_operation_location = response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    while True:
        result = client.get_read_result(operation_id)

        if result.status.lower () not in ['notstarted', 'running']:
            break
        print('waiting for image text extraction results...')
        time.sleep(10)

    if result.status == OperationStatusCodes.succeeded:
        results_list = []
        for text in result.analyze_result.read_results:
            for line in text.lines:
                results_list.append(line.text)
                # print(line.text)
                # print(line.bounding_box)
        print('finished extracting text from the image')
        return results_list

    print("Finished extracting text")

