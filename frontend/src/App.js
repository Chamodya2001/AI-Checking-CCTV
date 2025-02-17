import React from "react";
import LiveFeed from "./components/LiveFeed";
import UploadVideo from "./components/UploadVideo";

function App() {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold p-5 text-blue-700">CCTV Object Detection</h1>
      <div className="flex justify-center space-x-10">
        <LiveFeed />
        <UploadVideo />
      </div>
    </div>
  );
}

export default App;
