import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';  // Import Link for navigation

const LiveFeed = () => {
  const [isGunDetected, setIsGunDetected] = useState(false);
  const [isKnifeDetected, setIsKnifeDetected] = useState(false);
  const [alarmMessage, setAlarmMessage] = useState('');
  const [boundingBoxes, setBoundingBoxes] = useState([]);
  const [isVideoStarted, setIsVideoStarted] = useState(false);  // Track if video is started
  const audioRef = useRef(null);  // Reference for audio element

  useEffect(() => {
    if (isVideoStarted) {
      // Polling every 1 second to check if a gun or knife is detected
      const interval = setInterval(() => {
        fetch('http://127.0.0.1:5000/detection_status')
          .then(response => response.json())
          .then(data => {
            setIsGunDetected(data.gun_detected);
            setIsKnifeDetected(data.knife_detected);
            setBoundingBoxes(data.bounding_boxes);

            // Play the alarm sound only when a gun or knife is detected
            if (data.gun_detected) {
              setAlarmMessage('🚨 Gun detected! 🚨');
              // Play alarm for gun detection
              if (audioRef.current) {
                audioRef.current.play().catch((err) => {
                  console.error('Error playing sound:', err);
                });
              }
            } else if (data.knife_detected) {
              setAlarmMessage('🚨 Knife detected! 🚨');
              // Play alarm for knife detection
              if (audioRef.current) {
                audioRef.current.play().catch((err) => {
                  console.error('Error playing sound:', err);
                });
              }
            } else {
              setAlarmMessage('');
            }
          })
          .catch(err => console.error('Error fetching detection status', err));
      }, 1000);  // Poll every second

      return () => clearInterval(interval);
    }
  }, [isVideoStarted]);  // Only start polling after the video feed is started

  const startVideoFeed = () => {
    setIsVideoStarted(true);  // Start video feed when the user clicks the button
  };

  return (
    <div className="flex flex-col items-center">
      <h2 className="text-2xl mb-4">Live Video Feed</h2>

      {/* Navigation back to home */}
      <Link to="/">
        <button className="px-6 py-3 bg-gray-500 text-white rounded-lg mb-4">
          Back to Home
        </button>
      </Link>

      {/* Start button for user interaction */}
      {!isVideoStarted && (
        <button
          onClick={startVideoFeed}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg mb-4"
        >
          Start Live Video Feed
        </button>
      )}

      {/* Show live video feed only after start */}
      {isVideoStarted && (
        <img
          src="http://127.0.0.1:5000/video_feed"
          alt="Live feed"
          className="border border-gray-300 rounded-lg"
        />
      )}

      {/* Show alarm message if a gun or knife is detected */}
      {alarmMessage && (
        <div className="mt-4 text-red-600 font-bold text-xl">
          {alarmMessage}
        </div>
      )}

      {/* Render bounding boxes */}
      <div className="mt-4 relative">
        {boundingBoxes.map((box, index) => (
          <div
            key={index}
            className="absolute"
            style={{
              top: `${box[1]}px`,
              left: `${box[0]}px`,
              width: `${box[2] - box[0]}px`,
              height: `${box[3] - box[1]}px`,
              border: box[4] === 'gun' || box[4] === 'knife' ? '2px solid red' : '2px solid green',
            }}
          ></div>
        ))}
      </div>

      {/* Audio element for sound */}
      <audio ref={audioRef} preload="auto">
        <source src="/mixkit-classic-alarm-995.wav" type="audio/wav" />
        Your browser does not support the audio element.
      </audio>
    </div>
  );
};

export default LiveFeed;
