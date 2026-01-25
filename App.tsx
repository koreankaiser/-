
import React, { useEffect, useState } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Matching from './pages/Matching';
import Community from './pages/Community';
import ChatHub from './pages/ChatHub';
import Profile from './pages/Profile';
import BookUpload from './pages/BookUpload';
import ReadingStatusPage from './pages/ReadingStatus'; // 새로 추가
import { supabase } from './lib/supabase';

const App: React.FC = () => {
  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    // 현재 세션 가져오기
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    // 인증 상태 변화 감지
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <Router>
      <div className="antialiased text-gray-900">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={session ? <Navigate to="/dashboard" /> : <Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/matching" element={<Matching />} />
          <Route path="/community" element={<Community />} />
          <Route path="/chathub" element={<ChatHub />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/book-upload" element={<BookUpload />} />
          <Route path="/reading-status" element={<ReadingStatusPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
