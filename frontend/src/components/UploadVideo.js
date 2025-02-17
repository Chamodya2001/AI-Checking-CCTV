import React, { useState } from 'react';
import axios from 'axios';

const UploadVideo = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [detectionResults, setDetectionResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setVideoFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!videoFile) {
      alert('Please select a video file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', videoFile);

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/upload_video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;
      if (data.detections && data.detections.length > 0) {
        setDetectionResults(data.detections);
      } else {
        alert("No guns or knives detected.");
      }
    } catch (error) {
      console.error('Error uploading video:', error);
      alert('Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-video p-6">
      <h2 className="text-3xl font-bold text-green-600">Upload CCTV Video for Detection</h2>
      
      <form onSubmit={handleUpload} className="flex flex-col items-center">
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          className="border p-2 mt-4"
        />
        <button
          type="submit"
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
        >
          {loading ? 'Uploading...' : 'Upload Video'}
        </button>
      </form>

      {loading && <p className="mt-4">Processing video...</p>}

      {detectionResults.length > 0 && (
        <div className="mt-6">
          <h3 className="font-bold text-xl">Detection Results:</h3>
          <ul>
            {detectionResults.map((detection, index) => (
              <li key={index} className="mt-2">
                <strong>{detection.object}</strong> detected at{' '}
                {Math.round(detection.time)} seconds (Frame: {detection.frame})
                <br />
                Bounding Box: {JSON.stringify(detection.bounding_box)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default UploadVideo;
