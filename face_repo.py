import requests
import zipfile
import StringIO
import cloudinary
import cloudinary.uploader
import re
import config
from lib.log import logger
import os
import cv2


class FaceRepo(object):

    def __init__(self, base_path='.'):
        if not config.CLOUDINARY_URL:
            raise Exception('set CLOUDINARY_URL environment variable before creating FaceRepo instances')
        self.base_path = base_path
        self.face_data_dir = os.path.join(self.base_path, 'tmp', 'face-data')
        self.img_extn = '.jpg'

    def download_all(self):
        zip_file_url = cloudinary.utils.download_zip_url(prefixes='/')
        logger.info("source zip url: %s", zip_file_url)
        r = requests.get(zip_file_url, stream=True)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall(path=self.face_data_dir)

    def upload(self, imagepath, name):
        if not name:
            name = 'unknown'
        folder = '-'.join(re.split(r'\s+', name.lower()))
        if not os.path.exists(imagepath):
            logger.error('%s does not exists', imagepath)
            return
        res = cloudinary.uploader.upload(imagepath, folder=folder)
        logger.debug(res)

    def _folder_to_name(self, foldername):
        if foldername:
            return foldername.replace('-', ' ')

    def _name_to_folder(self, name):
        if name:
            return name.lower().replace(' ', '-')

    def _capitalize(self, name):
        words = name.split(' ')
        words = [chr(ord(word[0]) - 32) + word[1:] for word in words]
        return ' '.join(words)

    def get_faces_and_names(self):
        # Assuming every folder under tmp/ represents a person name seperated by `-`
        # All files inside ./tmp/firstname-secondname/* is a face image of the person with that name
        self.download_all()
        # parse the folder
        faces, labels = [], []
        dirname = self.face_data_dir
        if not os.path.exists(dirname):
            raise Exception('%s does not exists' % dirname)
        subjectsdir = [dname for dname in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, dname))]
        logger.info("subjectsdir %s", subjectsdir)
        names = [self._folder_to_name(subject) for subject in subjectsdir]
        logger.info("names %s", names)
        names = [self._capitalize(name) for name in names]
        logger.info("names %s", names)
        for folder, name in zip(subjectsdir, names):
            img_files = os.listdir(os.path.join(dirname, folder))
            logger.info("img_files %s", img_files)
            img_files = [img for img in img_files if img.endswith('%s' % self.img_extn)]
            logger.info("img_files %s", img_files)
            for img_file in img_files:
                img_path = os.path.join(dirname, folder, img_file)
                face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if face_img is not None:
                    faces.append(face_img)
                    labels.append(name)
        logger.info("faces loded are %s", set(labels))
        return faces, labels
