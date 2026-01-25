
import React, { useState } from 'react';
import Layout from '../components/Layout';
import { Search, Heart, UserCheck, MessageCircle } from 'lucide-react';

const Matching: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'DISCOVER' | 'RECEIVED'>('DISCOVER');

  const discoveryList = [
    { id: 1, name: '북매니아', book: '그리스인 조르바', trust: 99, match: 95 },
    { id: 2, name: '독서숲', book: '이기적 유전자', trust: 92, match: 88 },
    { id: 3, name: '지혜로운자', book: '연금술사', trust: 95, match: 82 },
  ];

  const receivedList = [
    { id: 4, name: '리더십킹', book: '데미안', trust: 98, message: '함께 읽으면서 깊은 대화 나눠보고 싶어요!' },
  ];

  return (
    <Layout>
      <div className="px-5 pt-8">
        <h2 className="text-2xl font-bold mb-6">북버디 찾기</h2>
        
        <div className="flex bg-white p-1 rounded-2xl mb-8 toss-card">
          <button
            onClick={() => setActiveTab('DISCOVER')}
            className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all ${
              activeTab === 'DISCOVER' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-400'
            }`}
          >
            탐색하기
          </button>
          <button
            onClick={() => setActiveTab('RECEIVED')}
            className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all ${
              activeTab === 'RECEIVED' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-400'
            }`}
          >
            받은 신청 <span className="ml-1 opacity-80 text-xs">1</span>
          </button>
        </div>

        {activeTab === 'DISCOVER' ? (
          <div className="space-y-4">
            <div className="relative mb-6">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="책 제목 또는 저자로 검색"
                className="w-full bg-white rounded-2xl py-4 pl-12 pr-4 text-sm toss-card border-none outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {discoveryList.map((item) => (
              <div key={item.id} className="toss-card p-5 flex flex-col">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    <img src={`https://picsum.photos/seed/p${item.id}/80/80`} className="w-12 h-12 rounded-full" />
                    <div>
                      <div className="flex items-center space-x-1">
                        <h4 className="font-bold text-gray-900">{item.name}</h4>
                        <span className="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">신뢰 {item.trust}%</span>
                      </div>
                      <p className="text-xs text-blue-600 font-semibold">{item.match}% 취향 일치</p>
                    </div>
                  </div>
                  <button className="text-gray-300 hover:text-red-400">
                    <Heart size={20} />
                  </button>
                </div>
                <div className="bg-gray-50 p-3 rounded-xl mb-4">
                  <p className="text-xs text-gray-400 mb-1">찾고 있는 책</p>
                  <p className="text-sm font-bold text-gray-800">{item.book}</p>
                </div>
                <button className="w-full toss-button-primary py-3 rounded-xl text-sm font-bold">
                  매칭 신청하기
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {receivedList.map((item) => (
              <div key={item.id} className="toss-card p-5 border-l-4 border-blue-500">
                <div className="flex items-center space-x-3 mb-4">
                  <img src={`https://picsum.photos/seed/p${item.id}/80/80`} className="w-12 h-12 rounded-full" />
                  <div>
                    <h4 className="font-bold text-gray-900">{item.name}</h4>
                    <p className="text-xs text-gray-500">신뢰도 {item.trust}% 독서가</p>
                  </div>
                </div>
                <div className="bg-blue-50 p-4 rounded-xl mb-4 text-sm text-gray-700 leading-relaxed italic">
                  "{item.message}"
                </div>
                <div className="flex space-x-2">
                  <button className="flex-1 bg-gray-100 py-3 rounded-xl text-sm font-bold text-gray-600">
                    거절
                  </button>
                  <button className="flex-1 toss-button-primary py-3 rounded-xl text-sm font-bold flex items-center justify-center">
                    <UserCheck size={18} className="mr-2" />
                    수락하기
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Matching;
