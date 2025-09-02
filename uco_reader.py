import csv
import cv2
from ultralytics import YOLO

class YOLOReader:
    def __init__(self, model_path="best.pt", cam_index=2, conf=0.7, csv_path="marker_mapping.csv"):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(cam_index)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        self.conf = conf
        
        # Read marker mapping from CSV
        self.marker_mapping = {}
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Handle potential spaces in column names
                    id_key = 'id'
                    value_key = 'value'
                    
                    # Check if columns have spaces
                    if ' id' in row:
                        id_key = ' id'
                    if ' value' in row:
                        value_key = ' value'
                    
                    self.marker_mapping[int(row[id_key])] = row[value_key]
        except FileNotFoundError:
            print(f"Warning: CSV file {csv_path} not found. Using default mapping.")
            # Fallback to default mapping if CSV is not found
            self.marker_mapping = {
                1: "809290",
                2: "165772",
                3: "325659", 
                4: "864335",
                5: "774586",
                6: "694842",
                7: "653677",
                8: "584515"
            }
        
        # Mapping from class names to numeric IDs
        self.class_to_id = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8
        }

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        results = self.model.predict(frame, conf=self.conf, verbose=False)

        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            cls_name = self.model.names[cls_id]
            conf = float(box.conf[0])
            detections.append({"class": cls_name, "confidence": conf})

        # keep only the detection with highest confidence
        top_detection = max(detections, key=lambda x: x["confidence"], default=None)

        # Return frame and UCO value (or None if no detection)
        if top_detection:
            # Convert class name to numeric ID and get value from mapping
            numeric_id = self.class_to_id.get(top_detection["class"])
            if numeric_id in self.marker_mapping:
                uco_value = self.marker_mapping[numeric_id]
                return frame, uco_value
        
        return frame, None

    def release(self):
        if self.cap.isOpened():
            self.cap.release()