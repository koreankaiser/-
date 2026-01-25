
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';

const Login: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isRegister) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: name },
          },
        });
        if (error) throw error;
        alert('회원가입이 완료되었습니다! 이메일을 확인해주세요.');
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        navigate('/dashboard');
      }
    } catch (error: any) {
      alert(error.message || '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white min-h-screen px-6 pt-20">
      <div className="mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          {isRegister ? '반가워요!\n함께 시작해볼까요?' : '어서오세요!\n다시 만나서 반가워요'}
        </h2>
        <p className="text-gray-500 whitespace-pre-line">
          {isRegister ? '북버디에서 새로운 친구들을 만나보세요.' : '북버디 로그인을 위해 정보를 입력해주세요.'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 ml-1">이메일 주소</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="example@email.com"
            className="w-full bg-gray-50 border-none rounded-2xl py-4 px-4 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 ml-1">비밀번호</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
            className="w-full bg-gray-50 border-none rounded-2xl py-4 px-4 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
        </div>

        {isRegister && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1 ml-1">이름</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="홍길동"
              className="w-full bg-gray-50 border-none rounded-2xl py-4 px-4 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className={`w-full toss-button-primary py-4 rounded-2xl font-bold text-lg mt-6 shadow-md ${loading ? 'opacity-50' : ''}`}
        >
          {loading ? '처리 중...' : (isRegister ? '가입하기' : '로그인')}
        </button>
      </form>

      <div className="mt-8 text-center">
        <button
          onClick={() => setIsRegister(!isRegister)}
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          {isRegister ? '이미 계정이 있으신가요?' : '아직 회원이 아니신가요?'}
        </button>
      </div>
    </div>
  );
};

export default Login;
