import cv2


def extract_faces(filepath, scale=1.2):
        from bot.app import f_cascade
        img_copy = cv2.imread(filepath)
        img_gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
        cordinates = f_cascade.detectMultiScale(img_gray,
                                                scaleFactor=scale,
                                                minNeighbors=5)
        if len(cordinates) == 0:
            return None, None
        faces_images = [img_gray[y:y + w, x:x + h] for (x, y, w, h) in cordinates]
        return faces_images, cordinates
