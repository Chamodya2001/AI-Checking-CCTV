import os
import cv2
import time
import threading
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

# Directories for storage
UPLOAD_FOLDER = 'uploads'
DETECTIONS_FOLDER = 'detections'
RECORDINGS_FOLDER = 'recordings'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DETECTIONS_FOLDER, exist_ok=True)
os.makedirs(RECORDINGS_FOLDER, exist_ok=True)

# Load YOLOv8 Model
model = YOLO("yolov8n.pt")

# Global variables
is_recording = False
video_writer = None
frame_width, frame_height, frame_fps = 640, 480, 20
detection_results = []
detection_lock = threading.Lock()  # Thread-safety

camera = cv2.VideoCapture(0)  # Open webcam

# Global variable to capture frame timestamp
frame_timestamp = None

def detect_objects():
    """Continuously detect objects from the live feed."""
    global is_recording, video_writer, detection_results, frame_timestamp
    frame_skip = 3
    frame_count = 0

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  # Skip frames to optimize performance

        frame_resized = cv2.resize(frame, (frame_width, frame_height))
        results = model(frame_resized)

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        temp_results = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0].item())
                label = model.names[cls]

                if label in ["gun", "knife"]:
                    # Draw red bounding box around detected object
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    temp_results.append({
                        "object": label,
                        "timestamp": timestamp,
                        "bounding_box": [x1, y1, x2, y2]
                    })

                    image_filename = f"{label}_{timestamp.replace(':', '-')}.jpg"
                    image_path = os.path.join(DETECTIONS_FOLDER, image_filename)
                    cv2.imwrite(image_path, frame)

        with detection_lock:
            detection_results.extend(temp_results)
            detection_results = detection_results[-50:]  # Keep only last 50 detections

        frame_timestamp = timestamp  # Update frame timestamp for frontend

        if is_recording and video_writer:
            video_writer.write(frame)

        # If a "gun" or "knife" is detected, play sound
        if temp_results:
            play_alert_sound()

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global is_recording, video_writer

    if is_recording:
        return jsonify({"error": "Already recording!"})

    video_filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}.avi"
    video_path = os.path.join(RECORDINGS_FOLDER, video_filename)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(video_path, fourcc, frame_fps, (frame_width, frame_height))
    is_recording = True

    return jsonify({"message": "Recording started!", "file": video_filename})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording, video_writer

    if not is_recording:
        return jsonify({"error": "No active recording!"})

    is_recording = False
    if video_writer:
        video_writer.release()
        video_writer = None

    return jsonify({"message": "Recording stopped!"})

@app.route('/detection_status', methods=['GET'])
def detection_status():
    with detection_lock:
        recent_detections = detection_results[-5:]

    return jsonify({"detections": recent_detections, "video_feed": "http://127.0.0.1:5000/video_feed", "timestamp": frame_timestamp})

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        while True:
            success, frame = camera.read()
            if not success:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detections/<filename>')
def get_detection_image(filename):
    return send_from_directory(DETECTIONS_FOLDER, filename)

def play_alert_sound():
    """Play the alarm sound when detecting a gun or knife."""
    os.system('aplay /path/to/sound/file.wav')  # Make sure the path to sound file is correct

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov', 'mkv'}

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_skip = 3
    frame_count = 0
    detections = []
    start_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        frame_resized = cv2.resize(frame, (640, 480))
        results = model(frame_resized)
        temp_detections = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0].item())
                label = model.names[cls]

                if label in ["gun", "knife"]:
                    detection_time = round(time.time() - start_time, 2)
                    temp_detections.append({
                        'object': label,
                        'time': detection_time,
                        'frame': frame_count,
                        'bounding_box': [x1, y1, x2, y2]
                    })
                    image_filename = f"frame_{frame_count}_time_{detection_time}.jpg"
                    image_path = os.path.join(DETECTIONS_FOLDER, image_filename)
                    cv2.imwrite(image_path, frame)

        detections.extend(temp_detections)

    cap.release()
    return detections

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"})

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    detections = process_video(filepath)

    for detection in detections:
        detection['image_url'] = f"/detections/frame_{detection['frame']}_time_{detection['time']}.jpg"

    return jsonify({"detections": detections})

if __name__ == '__main__':
    threading.Thread(target=detect_objects, daemon=True).start()
    app.run(debug=True)
