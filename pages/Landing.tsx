
import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookCheck, ShieldCheck, Zap } from 'lucide-react';

const Landing: React.FC = () => {
  return (
    <div className="bg-white min-h-screen flex flex-col items-center px-6 pt-24 pb-12 overflow-hidden">
      <div className="text-center space-y-6 max-w-sm mb-16">
        <h1 className="text-4xl font-bold tracking-[-0.01em] text-gray-900 leading-[1.3] break-keep">
          읽는 즐거움을 <br />
          <span className="toss-text-blue">나누는 즐거움으로</span>
        </h1>
        <p className="text-gray-500 text-lg break-keep">
          북버디에서 책을 매개로 <br />
          신뢰할 수 있는 친구를 만나보세요.
        </p>
        <div className="pt-8">
          <Link
            to="/login"
            className="w-full inline-flex items-center justify-center toss-button-primary py-4 px-8 rounded-2xl text-lg font-bold shadow-lg shadow-blue-200"
          >
            시작하기
            <ArrowRight className="ml-2" size={20} />
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 w-full max-w-md">
        <div className="p-6 toss-card flex items-start space-x-4">
          <div className="bg-blue-50 p-3 rounded-xl text-blue-600">
            <BookCheck size={24} />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">독서 메이트 매칭</h3>
            <p className="text-sm text-gray-500">같은 책을 읽는 사람들과 연결되어 생각을 나눠요.</p>
          </div>
        </div>

        <div className="p-6 toss-card flex items-start space-x-4">
          <div className="bg-green-50 p-3 rounded-xl text-green-600">
            <ShieldCheck size={24} />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">검증된 매너 점수</h3>
            <p className="text-sm text-gray-500">신뢰 기반의 활동으로 안전하고 쾌적한 커뮤니티.</p>
          </div>
        </div>

        <div className="p-6 toss-card flex items-start space-x-4">
          <div className="bg-yellow-50 p-3 rounded-xl text-yellow-600">
            <Zap size={24} />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">간편한 채팅 연결</h3>
            <p className="text-sm text-gray-500">매칭 성공 시 즉시 오픈채팅으로 대화 시작.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Landing;
