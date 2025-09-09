// next.config.js with Tailwind CSS v4 support
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Experimental features
  experimental: {
    // Performance optimizations
    optimizePackageImports: ['lucide-react', 'framer-motion'],
    optimizeCss: true,
    scrollRestoration: true,
    
    // Add other experimental features as needed
  },
  
  // Webpack configuration for Tailwind CSS v4
  webpack: (config) => {
    // Ensure PostCSS processes CSS files correctly
    config.module.rules.forEach((rule) => {
      if (rule.oneOf) {
        rule.oneOf.forEach((subRule) => {
          if (subRule.test && subRule.test.toString().includes('css')) {
            if (subRule.use && Array.isArray(subRule.use)) {
              const postcssLoader = subRule.use.find(
                (loader) => loader.loader && loader.loader.includes('postcss-loader')
              );
              if (postcssLoader) {
                // Make sure we are using the correct PostCSS config
                postcssLoader.options = {
                  ...postcssLoader.options,
                  postcssOptions: {
                    plugins: ['@tailwindcss/postcss', 'autoprefixer'],
                  },
                };
              }
            }
          }
        });
      }
    });
    
    return config;
  },
};

module.exports = nextConfig;
