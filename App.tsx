
import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Matching from './pages/Matching';
import Community from './pages/Community';
import ChatHub from './pages/ChatHub';
import Profile from './pages/Profile';
import BookUpload from './pages/BookUpload';

const App: React.FC = () => {
  return (
    <Router>
      <div className="antialiased text-gray-900">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/matching" element={<Matching />} />
          <Route path="/community" element={<Community />} />
          <Route path="/chathub" element={<ChatHub />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/book-upload" element={<BookUpload />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
