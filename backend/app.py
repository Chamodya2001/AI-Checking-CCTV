import os
import cv2
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import time

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# The folder to store detection images
DETECTIONS_FOLDER = 'detections'
os.makedirs(DETECTIONS_FOLDER, exist_ok=True)

# Load YOLOv8 Model (Replace with your specific model if it's custom-trained)
model = YOLO("yolov8n.pt")

@app.route('/detections/<filename>')
def get_detection_image(filename):
    """Serve the captured detection images"""
    return send_from_directory(DETECTIONS_FOLDER, filename)

# Function to check if file is an allowed video format
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        frame_resized = cv2.resize(frame, (640, 480))
        results = model(frame_resized)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0].item())

                if model.names[cls] == "knife":
                    detection_time = (time.time() - start_time)  # Time in seconds
                    detections.append({
                        'object': model.names[cls],
                        'time': detection_time,
                        'frame': frame_count,
                        'bounding_box': [x1, y1, x2, y2]
                    })

                    # Save the frame where the knife is detected
                    timestamp = round(detection_time, 2)  # Round to 2 decimal places for timestamp
                    image_filename = f"frame_{frame_count}_time_{timestamp}.jpg"
                    image_path = os.path.join(DETECTIONS_FOLDER, image_filename)
                    cv2.imwrite(image_path, frame)  # Save the image to the 'detections' folder

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

        # Return detections with the image URLs
        for detection in detections:
            timestamp = round(detection['time'], 2)
            detection['image_url'] = f"/detections/frame_{detection['frame']}_time_{timestamp}.jpg"
        
        return jsonify({"detections": detections})

    return jsonify({"error": "File type not allowed"})

if __name__ == '__main__':
    app.run(debug=True)
