
import React from 'react';
import Layout from '../components/Layout';
import { MOCK_POSTS } from '../constants';
import { ThumbsUp, MessageCircle, MoreHorizontal, PenLine } from 'lucide-react';

const Community: React.FC = () => {
  return (
    <Layout>
      <div className="px-5 pt-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">커뮤니티</h2>
          <button className="bg-blue-600 text-white p-2.5 rounded-2xl shadow-lg shadow-blue-100">
            <PenLine size={20} />
          </button>
        </div>

        {/* Trending Tags */}
        <div className="flex space-x-2 overflow-x-auto pb-4 scrollbar-hide">
          {['#추천도서', '#오늘의문장', '#독서모임', '#북버디모집'].map(tag => (
            <span key={tag} className="whitespace-nowrap bg-white px-4 py-2 rounded-full text-xs font-bold text-gray-500 border border-gray-100 shadow-sm">
              {tag}
            </span>
          ))}
        </div>

        <div className="space-y-4 mt-4 pb-10">
          {MOCK_POSTS.map(post => (
            <div key={post.id} className="toss-card p-5">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center space-x-3">
                  <img src={`https://picsum.photos/seed/${post.authorId}/80/80`} className="w-10 h-10 rounded-full" />
                  <div>
                    <h4 className="font-bold text-sm">{post.authorName}</h4>
                    <p className="text-[10px] text-gray-400">{post.createdAt}</p>
                  </div>
                </div>
                <button className="text-gray-300">
                  <MoreHorizontal size={20} />
                </button>
              </div>
              
              <p className="text-sm leading-relaxed text-gray-800 mb-6">
                {post.content}
              </p>

              <div className="flex items-center space-x-6 border-t border-gray-50 pt-4">
                <button className="flex items-center space-x-1.5 text-gray-400 hover:text-blue-500 transition-colors">
                  <ThumbsUp size={18} />
                  <span className="text-xs font-bold">{post.likes}</span>
                </button>
                <button className="flex items-center space-x-1.5 text-gray-400 hover:text-blue-500 transition-colors">
                  <MessageCircle size={18} />
                  <span className="text-xs font-bold">{post.comments}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default Community;
