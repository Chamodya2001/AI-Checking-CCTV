import os
import cv2
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load YOLOv8 Model (Replace with your specific model if it's custom-trained)
model = YOLO("yolov8n.pt")

# Function to check if file is an allowed video format
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Detect objects in video frames
def detect_objects(frame):
    """Detect objects in the frame and check for guns or knives"""
    frame_resized = cv2.resize(frame, (640, 480))

    results = model(frame_resized)
    bounding_boxes = []

    # Loop through detected objects
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0].item())

            # Check if the detected object is a gun or knife
            if model.names[cls] in ["gun", "knife"]:
                bounding_boxes.append([x1, y1, x2, y2, model.names[cls]])

            # Draw bounding boxes
            color = (0, 255, 0) if model.names[cls] not in ["gun", "knife"] else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, model.names[cls], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return frame, bounding_boxes

# Process video and detect guns and knives
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_skip = 3  # Skip every 3rd frame
    frame_count = 0
    detections = []

    start_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  # Skip the current frame

        # Detect objects in the frame
        frame, bounding_boxes = detect_objects(frame)

        # Log the detection with timestamps
        for box in bounding_boxes:
            detection_time = (time.time() - start_time)  # Time in seconds
            detections.append({
                'object': box[4],
                'time': detection_time,
                'frame': frame_count,
                'bounding_box': box[:4]
            })

    cap.release()
    return detections

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """Handle video upload"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the uploaded video
        detections = process_video(filepath)

        # Return detections (time frames of guns and knives detected)
        return jsonify({"detections": detections})

    return jsonify({"error": "File type not allowed"})

if __name__ == '__main__':
    app.run(debug=True)
