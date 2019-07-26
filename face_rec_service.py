import numpy as np
import cv2
from face_repo import FaceRepo
import config
import os
import time
from lib.log import logger


class FaceRecService(object):

    def __init__(self, base_path):
        self.base_path = base_path
        self.f_cascade = cv2.CascadeClassifier(os.path.join(base_path, config.CASCADE_FILE))
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_repo = FaceRepo(self.base_path)
        self.train()

    def train(self):
        faces, self.names = self.face_repo.get_faces_and_names()
        lables = np.array(list(range(len(self.names))))
        self.face_recognizer.train(faces, lables)

    def labelToName(self, label):
        if label < len(self.names):
            return self.names[label]

    def extract_faces(self, filename):
        img_copy = cv2.imread(filename)
        img_gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
        cordinates = self.f_cascade.detectMultiScale(img_gray,
                                                     scaleFactor=1.1,
                                                     minNeighbors=3)
        if len(cordinates) == 0:
            return []

        faces_images = [img_gray[y:y + w, x:x + h] for (x, y, w, h) in cordinates]
        face_filenames = [self._save_face_img(face) for face in faces_images]
        os.remove(filename)
        return face_filenames

    def _save_face_img(self, img):
        filename = str(time.time()) + config.IMG_EXTN
        filepath = os.path.join(self.base_path, 'tmp', 'faces', filename)
        cv2.imwrite(filepath, img)
        time.sleep(0.25)
        return filepath

    def predict(self, faceimg):
        # predict the image using our face recognizer
        prediction = self.face_recognizer.predict(cv2.imread(faceimg, cv2.IMREAD_GRAYSCALE))
        if prediction:
            lable, confidence = prediction
            if confidence <= 100:
                name = self.labelToName(lable)
                logger.info("prediction %s with %s confidence", name, round(100 - confidence))
                return '{} ({})'.format(name, confidence)
            else:
                return 'Unknown face'
