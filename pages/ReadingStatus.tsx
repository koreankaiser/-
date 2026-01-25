
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, ChevronLeft, Check } from 'lucide-react';
import Layout from '../components/Layout';

const ReadingStatus: React.FC = () => {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(65);
  const [memo, setMemo] = useState('');

  const handleUpdate = () => {
    // Supabase DB 업데이트 로직 (예시)
    // await supabase.from('books').update({ progress }).eq('id', bookId);
    alert('독서 기록이 저장되었습니다.');
    navigate('/dashboard');
  };

  return (
    <Layout showNav={false}>
      <div className="px-6 pt-10 pb-20">
        <header className="flex justify-between items-center mb-10">
          <button onClick={() => navigate(-1)} className="p-1">
            <ChevronLeft size={28} className="text-gray-900" />
          </button>
          <h2 className="text-lg font-bold">독서 기록</h2>
          <div className="w-7"></div>
        </header>

        <div className="space-y-10">
          {/* Book Info Card */}
          <div className="flex items-center space-x-4 p-4 toss-card">
            <img 
              src="https://picsum.photos/seed/demian/200/300" 
              className="w-16 h-22 rounded-md object-cover shadow-sm"
              alt="데미안"
            />
            <div>
              <h3 className="font-bold text-gray-900">데미안</h3>
              <p className="text-sm text-gray-400">헤르만 헤세</p>
            </div>
          </div>

          {/* Progress Slider */}
          <div className="space-y-6">
            <div className="flex justify-between items-end">
              <label className="text-sm font-bold text-gray-700">어디까지 읽으셨나요?</label>
              <span className="text-2xl font-bold toss-text-blue">{progress}%</span>
            </div>
            
            <div className="relative pt-1">
              <input
                type="range"
                min="0"
                max="100"
                value={progress}
                onChange={(e) => setProgress(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-[10px] text-gray-400 mt-2 font-medium">
                <span>0%</span>
                <span>25%</span>
                <span>50%</span>
                <span>75%</span>
                <span>100%</span>
              </div>
            </div>
          </div>

          {/* Short Memo */}
          <div className="space-y-3">
            <label className="text-sm font-bold text-gray-700 ml-1">오늘의 한 줄 평 (선택)</label>
            <textarea
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="읽으면서 느낀 점을 짧게 기록해보세요."
              className="w-full bg-white toss-card p-5 border-none outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px] text-sm resize-none"
            />
          </div>

          <button
            onClick={handleUpdate}
            className="w-full toss-button-primary py-4 rounded-2xl font-bold text-lg shadow-lg shadow-blue-100 flex items-center justify-center"
          >
            <Check size={20} className="mr-2" />
            기록 완료
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default ReadingStatus;
