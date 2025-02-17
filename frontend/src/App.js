import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';
import UploadVideo from './components/UploadVideo';
import LiveFeed from './components/LiveFeed';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload" element={<UploadVideo />} />
        <Route path="/livefeed" element={<LiveFeed />} />
      </Routes>
    </Router>
  );
};

export default App;
