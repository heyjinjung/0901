require('@testing-library/jest-dom');

const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    const msg = args.join(' ');
    if (typeof msg === 'string' && msg.includes('Warning:')) return;
    originalError(...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
