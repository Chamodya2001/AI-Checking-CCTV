import React, { useState, useEffect, useRef } from 'react';

const LiveFeed = () => {
  const [detections, setDetections] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [timestamp, setTimestamp] = useState('');
  const audioRef = useRef(null);

  useEffect(() => {
    // Fetch detection status every second
    const interval = setInterval(() => {
      fetch('http://127.0.0.1:5000/detection_status')
        .then(res => res.json())
        .then(data => {
          setDetections(data.detections);
          setTimestamp(data.timestamp);
          
          // Play sound if an object like gun or knife is detected
          const latestDetection = data.detections[data.detections.length - 1];
          if (latestDetection && (latestDetection.object === "gun" || latestDetection.object === "knife")) {
            audioRef.current.play().catch(err => console.log("Error playing sound:", err));
          }
        })
        .catch(err => console.error('Error fetching detection status:', err));
    }, 1000); // Update every 1 second

    return () => clearInterval(interval);  // Clean up on unmount
  }, []);

  const toggleRecording = () => {
    const endpoint = isRecording ? "stop_recording" : "start_recording";
    fetch(`http://127.0.0.1:5000/${endpoint}`, { method: "POST" })
      .then(res => res.json())
      .then(() => setIsRecording(!isRecording));
  };

  return (
    <div className="p-4 text-center">
      <h2 className="text-xl font-bold">Live Video Feed</h2>
      <img src="http://127.0.0.1:5000/video_feed" alt="Live Feed" className="w-full max-w-xl border rounded" />

      <button onClick={toggleRecording} className="mt-4 p-2 bg-blue-600 text-white rounded">
        {isRecording ? "Stop Recording" : "Start Recording"}
      </button>

      <h3 className="mt-2 text-lg font-semibold">Detection Status (Last 5 detections)</h3>
      <ul className="mt-4">
        {detections.map((det, index) => (
          <li key={index} className={`text-lg ${det.object === "gun" || det.object === "knife" ? "text-red-600" : "text-green-600"}`}>
            {det.timestamp}: {det.object} detected!
            <div>
              {/* Bounding Box Visualization: */}
              <div
                className="absolute"
                style={{
                  left: `${det.bounding_box[0]}px`,
                  top: `${det.bounding_box[1]}px`,
                  width: `${det.bounding_box[2] - det.bounding_box[0]}px`,
                  height: `${det.bounding_box[3] - det.bounding_box[1]}px`,
                  border: '2px solid red',
                  position: 'absolute',
                }}
              ></div>
            </div>
          </li>
        ))}
      </ul>

      {/* Audio alert sound */}
      <audio ref={audioRef} src="/mixkit-classic-alarm-995.wav" preload="auto"></audio>
    </div>
  );
};

export default LiveFeed;
