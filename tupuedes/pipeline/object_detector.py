from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from tupuedes.pipeline import Pipeline
import mediapipe as mp
import numpy as np
import cv2

class ObjectDetector(Pipeline):
    def __init__(self):
        # STEP 2: Create an ObjectDetector object.
        base_options = python.BaseOptions(model_asset_path='models/efficientdet_lite2_fp32.tflite')
        options = vision.ObjectDetectorOptions(base_options=base_options,
                                               score_threshold=0.5)
        self.detector = vision.ObjectDetector.create_from_options(options)
        super().__init__()
    def map(self, data):
        data = self.detect(data)

        return data

    def detect(self, data):
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=data["image"])

        # STEP 4: Detect objects in the input image.
        detection_result = self.detector.detect(image)

        # STEP 5: Process the detection result. In this case, visualize it.
        image_copy = np.copy(image.numpy_view())
        annotated_image = self.visualize(image_copy, detection_result)
        #rgb_annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

        data["image"] = annotated_image

        return data

    def visualize(self,
            image,
            detection_result
    ) -> np.ndarray:
        """Draws bounding boxes on the input image and return it.
        Args:
          image: The input RGB image.
          detection_result: The list of all "Detection" entities to be visualize.
        Returns:
          Image with bounding boxes.
        """
        MARGIN = 20  # pixels
        ROW_SIZE = 25  # pixels
        FONT_SIZE = 3
        FONT_THICKNESS = 3
        TEXT_COLOR = (0, 0, 255)  # red

        for detection in detection_result.detections:
            # Draw bounding_box
            bbox = detection.bounding_box
            start_point = bbox.origin_x, bbox.origin_y
            end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
            cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

            # Draw label and score
            category = detection.categories[0]
            category_name = category.category_name
            probability = round(category.score, 2)
            result_text = category_name + ' (' + str(probability) + ')'
            text_location = (MARGIN + bbox.origin_x,
                             MARGIN + ROW_SIZE + bbox.origin_y)
            cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                        FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

        return image