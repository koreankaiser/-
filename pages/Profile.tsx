
import React from 'react';
import Layout from '../components/Layout';
import { Settings, Edit2, Shield, Share2, LogOut } from 'lucide-react';
import { MOCK_USER } from '../constants';
import { useNavigate } from 'react-router-dom';

const Profile: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Layout>
      <div className="px-5 pt-8 pb-10">
        <div className="flex justify-between items-start mb-8">
          <h2 className="text-2xl font-bold">프로필</h2>
          <button className="p-2 text-gray-400">
            <Settings size={24} />
          </button>
        </div>

        {/* Profile Card */}
        <div className="toss-card p-6 flex flex-col items-center mb-6">
          <div className="relative mb-4">
            <img 
              src={MOCK_USER.profileImage} 
              alt="Profile" 
              className="w-24 h-24 rounded-full shadow-md object-cover" 
            />
            <button className="absolute bottom-0 right-0 bg-white p-1.5 rounded-full shadow-sm border border-gray-100 text-blue-600">
              <Edit2 size={16} />
            </button>
          </div>
          <h3 className="text-xl font-bold">{MOCK_USER.name}</h3>
          <p className="text-sm text-gray-500 mb-6">{MOCK_USER.email}</p>
          
          <div className="grid grid-cols-3 w-full border-t border-gray-100 pt-6">
            <div className="text-center">
              <p className="text-lg font-bold">12</p>
              <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">독서량</p>
            </div>
            <div className="text-center border-x border-gray-100">
              <p className="text-lg font-bold">45</p>
              <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">포스트</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold">8</p>
              <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">매칭완료</p>
            </div>
          </div>
        </div>

        {/* Trust Score Card */}
        <div className="toss-card p-6 bg-gray-50 mb-8">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center space-x-2">
              <Shield size={18} className="text-blue-500" />
              <span className="font-bold text-sm">독서 신뢰도</span>
            </div>
            <span className="text-blue-600 font-bold">{MOCK_USER.trustScore}점</span>
          </div>
          <div className="w-full bg-gray-200 h-2 rounded-full mb-3">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${MOCK_USER.trustScore}%` }}></div>
          </div>
          <p className="text-xs text-gray-400">신뢰도가 높을수록 더 많은 북버디 추천을 받을 수 있어요.</p>
        </div>

        {/* Menu List */}
        <div className="space-y-3">
          <button className="w-full toss-card p-4 flex items-center justify-between text-sm font-medium">
            <span>나의 오픈채팅 링크 관리</span>
            <Share2 size={16} className="text-gray-300" />
          </button>
          <button className="w-full toss-card p-4 flex items-center justify-between text-sm font-medium text-red-500" onClick={() => navigate('/')}>
            <span>로그아웃</span>
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default Profile;
