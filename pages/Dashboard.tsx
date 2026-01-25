
import React, { useEffect, useState } from 'react';
import { Plus, ChevronRight, TrendingUp, Info } from 'lucide-react';
import Layout from '../components/Layout';
import { MOCK_BOOKS, MOCK_USER } from '../constants';
import { Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { Book } from '../types';

const Dashboard: React.FC = () => {
  const [books, setBooks] = useState<Book[]>(MOCK_BOOKS);
  const [isDemo, setIsDemo] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSupabase = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.user) {
          setIsDemo(false);
          const { data, error } = await supabase
            .from('books')
            .select('*')
            .eq('uploaderId', session.user.id);
            
          if (!error && data && data.length > 0) {
            setBooks(data);
          }
        }
      } catch (err) {
        console.error('Auth check failed:', err);
      } finally {
        setLoading(false);
      }
    };
    checkSupabase();
  }, []);

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="animate-pulse flex flex-col items-center">
            <div className="w-12 h-12 bg-gray-200 rounded-full mb-4"></div>
            <div className="h-4 w-24 bg-gray-200 rounded"></div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="px-5 pt-8 space-y-8">
        {isDemo && (
          <div className="bg-blue-50 p-4 rounded-2xl border border-blue-100 flex items-start space-x-3">
            <Info size={18} className="text-blue-500 mt-0.5" />
            <div>
              <p className="text-xs text-blue-800 font-bold mb-0.5">데모 모드 안내</p>
              <p className="text-[11px] text-blue-600 leading-relaxed">
                현재 Supabase 연결 전입니다. 미리 준비된 데이터를 통해 기능을 둘러보실 수 있습니다.
              </p>
            </div>
          </div>
        )}

        {/* Header/Welcome */}
        <section>
          <div className="flex justify-between items-end mb-4">
            <div>
              <p className="text-gray-500 font-medium">안녕하세요</p>
              <h2 className="text-2xl font-bold">{MOCK_USER.name}님, 오늘도 즐거운 독서되세요!</h2>
            </div>
            <div className="bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-xs font-bold border border-blue-100">
              신뢰도 {MOCK_USER.trustScore}%
            </div>
          </div>
        </section>

        {/* Current Reading */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-900">내 독서 상태</h3>
            <Link to="/book-upload" className="text-blue-600 p-1 hover:bg-blue-50 rounded-lg transition-colors">
              <Plus size={24} />
            </Link>
          </div>
          
          <div className="space-y-4">
            {books.filter(b => b.status === 'READING').length > 0 ? (
              books.filter(b => b.status === 'READING').map(book => (
                <div key={book.id} className="toss-card p-5 flex space-x-4">
                  <img src={book.coverImage} alt={book.title} className="w-20 h-28 rounded-lg object-cover shadow-sm" />
                  <div className="flex-1 flex flex-col justify-between py-1">
                    <div>
                      <h4 className="font-bold text-lg leading-tight">{book.title}</h4>
                      <p className="text-gray-400 text-sm">{book.author}</p>
                    </div>
                    <div className="space-y-2">
                      <div className="w-full bg-gray-100 h-2 rounded-full">
                        <div className="bg-blue-500 h-2 rounded-full w-[65%]"></div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-blue-600 font-bold">65% 읽음</span>
                        <Link to="/reading-status" className="text-xs text-gray-400 flex items-center">
                          기록하기 <ChevronRight size={12} />
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="toss-card p-10 text-center">
                <p className="text-gray-400 text-sm">등록된 책이 없습니다.</p>
                <Link to="/book-upload" className="text-blue-600 text-xs font-bold mt-2 inline-block">첫 책 등록하기</Link>
              </div>
            )}
          </div>
        </section>

        {/* Quick Matching */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-900">추천 북버디</h3>
            <Link to="/matching" className="text-sm text-gray-400 flex items-center">
              전체보기 <ChevronRight size={14} />
            </Link>
          </div>
          
          <div className="flex space-x-4 overflow-x-auto pb-2 scrollbar-hide">
            {[1, 2, 3].map((i) => (
              <div key={i} className="min-w-[140px] toss-card p-4 flex flex-col items-center text-center">
                <img 
                  src={`https://picsum.photos/seed/buddy${i}/100/100`} 
                  alt="User" 
                  className="w-16 h-16 rounded-full mb-3 border-2 border-white ring-1 ring-gray-100" 
                />
                <p className="font-bold text-sm">독서왕{i}</p>
                <p className="text-xs text-blue-500 font-semibold mb-3">{90+i}% 일치</p>
                <button className="w-full py-2 bg-gray-50 hover:bg-gray-100 rounded-xl text-xs font-bold transition-colors">
                  신청하기
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Insights */}
        <section className="pb-10">
          <div className="toss-card p-6 bg-gradient-to-br from-blue-600 to-blue-500 text-white">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp size={20} />
              <span className="text-sm font-medium opacity-90">이번 달 독서 분석</span>
            </div>
            <p className="text-xl font-bold leading-snug">
              김버디님은 이번 달<br /> 
              상위 5% 독서가입니다. 👏
            </p>
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default Dashboard;
