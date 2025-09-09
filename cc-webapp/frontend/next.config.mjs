/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable Next.js Dev Tools overlay in development to avoid DOM replacement
  // that interferes with Playwright a11y/SEO checks.
  devIndicators: false,
};

export default nextConfig;
