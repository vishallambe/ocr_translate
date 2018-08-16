# import the necessary packages
from imutils.video import VideoStream
import argparse
import time
import cv2
from urllib2 import urlopen
import imutils
import numpy as np
import io
import PIL
from PIL import Image
import os, shutil
import Image
from pytesseract import image_to_string
# Imports the Google Cloud client library
from google.cloud import translate
from google.cloud import vision_v1p3beta1 as vision

def detect_handwritten_ocr(path):
    """Detects handwritten characters in a local image.

    Args:
    path: The path to the local file.
    """

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Language hint codes for handwritten OCR:
    # en-t-i0-handwrit, mul-Latn-t-i0-handwrit
    # Note: Use only one language hint code per request for handwritten OCR.
    image_context = vision.types.ImageContext(
        language_hints=['en-t-i0-handwrit'])

    response = client.document_text_detection(image=image,
                                              image_context=image_context)

    #print('Full Text: {}'.format(response.full_text_annotation.text))

    return(response.full_text_annotation.text)


def translate_text(text,target):
    # Instantiates a client
    translate_client = translate.Client()

    # Translates some text into Russian
    translation = translate_client.translate(
        text,
        target_language=target)

    print(u'Text: {}'.format(text))
    print(u'Translation: {}'.format(translation['translatedText']))

def main():

    host = 'http://10.0.0.220:8080/'
    url = host + 'shot.jpg'
    folder = '/home/vishal/Documents/git_repo/ocr_translate/images/'


    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True,
                    help="Source of video stream (webcam/host)")
    args = vars(ap.parse_args())

    if args["source"] == "webcam":
        capture = cv2.VideoCapture(0)

    time.sleep(2.0)

    i = 0

    # keep looping over the frames
    while True:

        # grab the current frame and then handle if the frame is returned
        # from either the 'VideoCapture' or 'VideoStream' object,
        # respectively
        if args["source"] == "webcam":
            ret, frame = capture.read()
        else:
            imgResp = urlopen(url)
            imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
            frame = cv2.imdecode(imgNp, -1)

        frame = imutils.resize(frame, width=800)
        cv2.imshow("Translation Application", frame)

        #cv2.imwrite('/home/vishal/Documents/git_repo/ocr_translate/images/image'.format(i), frame)
        cv2.imwrite("/home/vishal/Documents/git_repo/ocr_translate/images/image%04i.jpg"%i, frame)

        #use tressaract to check if text exists in the image.. if exists, call google api
        if image_to_string(Image.open("/home/vishal/Documents/git_repo/ocr_translate/images/image%04i.jpg"%i)) != '':
            detected_text = detect_handwritten_ocr("/home/vishal/Documents/git_repo/ocr_translate/images/image%04i.jpg"%i)
            print(detected_text)

            translate_text(detected_text,'mr')

        i=i+1;

       # time.sleep(2.0)

        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)
            break

    # close the output CSV file do a bit of cleanup
    print("[INFO] cleaning up...")

    cv2.destroyAllWindows()

if __name__ == '__main__': main()
