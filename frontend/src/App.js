import React from 'react';
import HomePage from './HomePage';
import UploadVideo from './components/UploadVideo';
import LiveFeed from './components/LiveFeed';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

const App = () => {
  return (
    <Router future={{ v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload" element={<UploadVideo />} />
        <Route path="/live" element={<LiveFeed />} />
      </Routes>
    </Router>
  );
};

export default App;

