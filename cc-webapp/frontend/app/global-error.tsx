'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-black">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-red-400 mb-4">오류가 발생했습니다</h1>
          <p className="text-white text-lg mb-8">{error.message}</p>
          <button
            onClick={reset}
            className="px-6 py-3 bg-red-400 text-black rounded-lg hover:bg-red-300 transition-colors"
          >
            다시 시도
          </button>
        </div>
      </body>
    </html>
  );
}
