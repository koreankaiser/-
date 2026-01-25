
import React from 'react';
import Layout from '../components/Layout';
import { ExternalLink, MessageSquare, AlertCircle } from 'lucide-react';

const ChatHub: React.FC = () => {
  const activeChats = [
    { id: 1, partner: '리더십킹', book: '데미안', status: 'ACTIVE', url: 'https://open.kakao.com/o/s12345' },
    { id: 2, partner: '독서숲', book: '이기적 유전자', status: 'ACTIVE', url: 'https://open.kakao.com/o/s67890' },
  ];

  return (
    <Layout>
      <div className="px-5 pt-8">
        <h2 className="text-2xl font-bold mb-6">채팅 허브</h2>

        <div className="bg-blue-50 p-4 rounded-2xl border border-blue-100 flex items-start space-x-3 mb-8">
          <AlertCircle className="text-blue-500 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-xs text-blue-700 leading-relaxed font-medium">
            매칭이 수락되면 상대방의 카카오톡 오픈채팅 링크가 여기에 나타납니다. 링크를 클릭하여 대화를 시작해보세요.
          </p>
        </div>

        <div className="space-y-4">
          {activeChats.length > 0 ? (
            activeChats.map(chat => (
              <div key={chat.id} className="toss-card p-5 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-2xl bg-blue-100 flex items-center justify-center text-blue-600">
                    <MessageSquare size={24} />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900">{chat.partner}</h4>
                    <p className="text-xs text-gray-500">책: {chat.book}</p>
                  </div>
                </div>
                <a 
                  href={chat.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="bg-gray-50 p-3 rounded-xl text-blue-600 hover:bg-blue-50 transition-colors"
                >
                  <ExternalLink size={20} />
                </a>
              </div>
            ))
          ) : (
            <div className="text-center py-20">
              <p className="text-gray-400 font-medium">아직 활성화된 채팅이 없습니다.</p>
              <p className="text-xs text-gray-400 mt-2">마음에 드는 버디를 찾아 매칭을 신청해보세요!</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default ChatHub;
