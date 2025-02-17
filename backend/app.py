import os
import cv2
from flask import Flask, Response, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load YOLOv8 Model
model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0)  # Live webcam
cell_phone_detected = False
bounding_boxes = []  # Store bounding box coordinates for detected objects

def detect_objects():
    """Detect objects in live feed"""
    global cell_phone_detected, bounding_boxes
    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame)
        cell_phone_detected = False
        bounding_boxes = []  # Reset bounding boxes

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0].item())

                color = (0, 255, 0)  # Default green color for other objects
                if model.names[cls] == "cell phone":
                    color = (0, 0, 255)  # Red color for cell phone
                    cell_phone_detected = True

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)  # Draw bounding box
                cv2.putText(frame, model.names[cls], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Return bounding box and detection status
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Live video stream"""
    return Response(detect_objects(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cell_phone_status')
def cell_phone_status():
    """Return cell phone detection status"""
    return jsonify({"cell_phone_detected": cell_phone_detected, "bounding_boxes": bounding_boxes})

if __name__ == '__main__':
    app.run(debug=True)
