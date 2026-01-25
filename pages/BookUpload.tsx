
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Upload, X, Check } from 'lucide-react';
import Layout from '../components/Layout';

const BookUpload: React.FC = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = () => {
    // Logic to save book
    alert('책이 등록되었습니다!');
    navigate('/dashboard');
  };

  return (
    <Layout showNav={false}>
      <div className="px-6 pt-10 pb-20">
        <header className="flex justify-between items-center mb-8">
          <button onClick={() => navigate(-1)} className="p-1">
            <X size={28} className="text-gray-400" />
          </button>
          <h2 className="text-lg font-bold">책 등록하기</h2>
          <div className="w-7"></div> {/* Spacer */}
        </header>

        <div className="space-y-8">
          <div className="flex flex-col items-center">
            <div className="relative w-48 h-64 bg-gray-100 rounded-2xl flex flex-col items-center justify-center overflow-hidden border-2 border-dashed border-gray-200 group">
              {preview ? (
                <img src={preview} alt="Preview" className="w-full h-full object-cover" />
              ) : (
                <>
                  <Camera size={40} className="text-gray-300 mb-2" />
                  <p className="text-xs text-gray-400">책 표지 촬영 또는 업로드</p>
                </>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 ml-1">책 제목</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="어떤 책인가요?"
                className="w-full bg-white border-none toss-card py-4 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 ml-1">저자</label>
              <input
                type="text"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                placeholder="누가 썼나요?"
                className="w-full bg-white border-none toss-card py-4 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={!title || !author}
            className={`w-full py-4 rounded-2xl font-bold text-lg mt-6 shadow-md transition-all ${
              title && author ? 'toss-button-primary' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            등록 완료
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default BookUpload;
