
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, BookOpen, Users, MessageSquare, User } from 'lucide-react';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: '홈', icon: Home },
    { path: '/matching', label: '매칭', icon: BookOpen },
    { path: '/community', label: '커뮤니티', icon: Users },
    { path: '/chathub', label: '채팅', icon: MessageSquare },
    { path: '/profile', label: '프로필', icon: User },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 px-4 pb-safe z-50">
      <div className="max-w-md mx-auto flex justify-between items-center py-3">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex flex-col items-center space-y-1 transition-colors ${
              isActive(item.path) ? 'text-blue-600 font-semibold' : 'text-gray-400'
            }`}
          >
            <item.icon size={22} strokeWidth={isActive(item.path) ? 2.5 : 2} />
            <span className="text-[10px]">{item.label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default Navigation;
