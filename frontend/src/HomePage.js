import React, { useState } from 'react';
import { Link } from 'react-router-dom';  // Import Link for navigation

const HomePage = () => {
  return (
    <div className="home-page flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold text-green-600 mb-8">CCTV Detection System</h1>

      {/* Links to navigate to Upload or Live Detection */}
      <div className="options flex flex-col items-center">
        <Link to="/upload">
          <button className="px-4 py-2 bg-blue-500 text-white rounded mb-4">
            Upload Video
          </button>
        </Link>
        <Link to="/live">
          <button className="px-4 py-2 bg-blue-500 text-white rounded">
            Live Detection
          </button>
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
