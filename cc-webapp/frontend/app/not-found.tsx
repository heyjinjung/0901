'use client';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-black">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-cyan-400 mb-4">404</h1>
        <p className="text-white text-xl mb-8">페이지를 찾을 수 없습니다</p>
        <button
          onClick={() => (window.location.href = '/')}
          className="px-6 py-3 bg-cyan-400 text-black rounded-lg hover:bg-cyan-300 transition-colors"
        >
          홈으로 돌아가기
        </button>
      </div>
    </div>
  );
}
