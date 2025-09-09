/**
 * Temporary build config to unblock release:
 * - Ignore ESLint and TS build errors (to be re-enabled post-release)
 * - Provide alias for next-themes shim (React 19 peer conflict workaround)
 */
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['images.unsplash.com'],
  },
  // Produce standalone output for Docker runtime (copies minimal server + node_modules)
  output: 'standalone',
  typescript: {
  ignoreBuildErrors: false,
  },
  eslint: {
    // 루트 .eslintrc와 충돌로 빌드 실패 방지 (CI에서 별도 lint 실행)
    ignoreDuringBuilds: true,
  },
  reactStrictMode: false,
  useFileSystemPublicRoutes: true,
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  async rewrites() {
    // Proxy frontend /api/* to real backend API to support tests like page.request('/api/...')
    // Prefer internal URL for server-side access inside Docker; fallback to public origin, then localhost
    const internal = process.env.NEXT_PUBLIC_API_URL_INTERNAL;
    const publicOrigin = process.env.NEXT_PUBLIC_API_ORIGIN;
    const base = internal || publicOrigin || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${base.replace(/\/$/, '')}/api/:path*`,
      },
    ];
  },
  webpack: (config) => {
    config.resolve = config.resolve || {};
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
  '@': require('path').resolve(__dirname),
      'next-themes': require('path').resolve(__dirname, 'types/shims/next-themes.ts'),
    };
    // 과도한 디렉토리 워치로 인한 메모리 사용 감소 목적 ignore
    config.watchOptions = {
      ...(config.watchOptions || {}),
      ignored: [
        '**/logs/**',
        '**/data/**',
        '**/test-results/**',
        '**/node_modules/**/.cache/**'
      ],
    };
    return config;
  },
};

module.exports = nextConfig;
