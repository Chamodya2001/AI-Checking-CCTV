import React, { useState } from "react";
import axios from "axios";

const UploadVideo = () => {
  const [file, setFile] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://127.0.0.1:5000/upload_video", formData);
      alert("Video uploaded successfully!");
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-green-600">Upload CCTV Video</h1>
      <form onSubmit={handleUpload} className="flex flex-col items-center">
        <input type="file" onChange={(e) => setFile(e.target.files[0])} className="border p-2 mt-4" />
        <button type="submit" className="mt-3 px-4 py-2 bg-green-500 text-white rounded-lg">Upload & Detect</button>
      </form>
    </div>
  );
};

export default UploadVideo;
