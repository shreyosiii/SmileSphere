import random
import os
import logging
import cv2
import numpy as np
import urllib.request


class SmileDetector:
    """Smile detection with deep learning face detection"""

    def __init__(self):   # <-- FIXED
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Create models directory if not exists
        self.model_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.model_dir, exist_ok=True)

        # File paths
        self.configFile = os.path.join(self.model_dir, "deploy.prototxt")
        self.modelFile = os.path.join(self.model_dir, "res10_300x300_ssd_iter_140000.caffemodel")

        # Download models if not already present
        self._download_models()

        # Load DNN face detector
        self.face_net = cv2.dnn.readNetFromCaffe(self.configFile, self.modelFile)

        # Haar cascade for smiles only
        haar_path = cv2.data.haarcascades
        self.smile_cascade = cv2.CascadeClassifier(os.path.join(haar_path, "haarcascade_smile.xml"))

    def _download_models(self):
        """Download model files if missing"""
        if not os.path.exists(self.configFile):
            self.logger.info("Downloading deploy.prototxt...")
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
                self.configFile
            )
        if not os.path.exists(self.modelFile):
            self.logger.info("Downloading res10_300x300_ssd_iter_140000.caffemodel...")
            urllib.request.urlretrieve(
                "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/"
                "res10_300x300_ssd_iter_140000.caffemodel",
                self.modelFile
            )

    def detect_faces(self, image):
        """Detect faces using OpenCV DNN"""
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        self.face_net.setInput(blob)
        detections = self.face_net.forward()

        faces = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.6:  # Only accept strong detections
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")
                faces.append((x1, y1, x2 - x1, y2 - y1))
        return faces

    def calculate_smile_score(self, image_data):
        """Detect smile and return score"""
        try:
            # Load image
            if isinstance(image_data, str) and os.path.exists(image_data):
                image = cv2.imread(image_data)
            elif isinstance(image_data, bytes):
                image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            else:
                return 0, "Unsupported image data type"

            if image is None:
                return 0, "Invalid image file"

            # Detect faces
            faces = self.detect_faces(image)
            if len(faces) == 0:
                return 0, "No human face detected"

            # Check smiles in detected faces
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                smiles = self.smile_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.8,
                    minNeighbors=25,
                    minSize=(30, 30)
                )
                if len(smiles) > 0:
                    return random.randint(7, 10), "Smile detected"

            return random.randint(1, 3), "Face detected, no strong smile"

        except Exception as e:
            self.logger.error(f"Error in smile detection: {str(e)}")
            return 0, f"Error: {str(e)}"

    def analyze_image(self, image_path_or_data):
        score, message = self.calculate_smile_score(image_path_or_data)

        if score == 0:
            feedback = message
        elif score <= 3:
            feedback = "We detected a slight smile. Try showing more teeth!"
        elif score <= 6:
            feedback = "Nice smile! You're doing great."
        elif score <= 9:
            feedback = "Fantastic smile! Your happiness is contagious."
        else:
            feedback = "Perfect smile! You've mastered the art of smiling."

        return {
            "score": score,
            "message": message,
            "feedback": feedback
        }


if __name__ == "__main__":   # <-- FIXED
    detector = SmileDetector()
    import sys
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
        result = detector.analyze_image(test_image)
        print(f"Smile Score: {result['score']}/10")
        print(f"Message: {result['message']}")
        print(f"Feedback: {result['feedback']}")
    else:
        print("Please provide an image path for testing")
