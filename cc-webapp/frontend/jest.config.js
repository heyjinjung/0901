/** Minimal Jest config for frontend unit tests */
const nextJest = require('next/jest');

const createJestConfig = nextJest({ dir: './' });

/** @type {import('jest').Config} */
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'].filter(Boolean),
  testMatch: ['**/__tests__/**/*.test.{ts,tsx,js}'],
  moduleFileExtensions: ['tsx', 'ts', 'js', 'jsx', 'json'],
  moduleNameMapper: {
    '^@/store/globalStore$': '<rootDir>/store/globalStore.tsx',
    '^@/(.+)$': '<rootDir>/$1',
    '^react$': '<rootDir>/node_modules/react',
    '^react-dom$': '<rootDir>/node_modules/react-dom',
    '^react-dom/server$': 'react-dom/server.node',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
    testEnvironment: 'jsdom',
  testPathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/',
    '<rootDir>/tests/e2e/',
    '<rootDir>/e2e/',
    '<rootDir>/playwright/',
    '<rootDir>/tests/playwright/',
    '\\.(pw|e2e)\\.(test|spec)$'
  ],
};

module.exports = createJestConfig(customJestConfig);
