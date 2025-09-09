
const { JSDOM } = require('jsdom');
const React = require('react');
const { render, screen, waitFor, act } = require('@testing-library/react');
const moduleExport = require('../components/NotificationToast.tsx');
const ToastProvider = moduleExport.default || moduleExport.ToastProvider;

test('ToastProvider dedupe 및 children 오류 검증', async () => {
  jest.useFakeTimers();
  // Setup JSDOM global
  const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', { url: 'http://localhost' });
  global.window = dom.window;
  global.document = dom.window.document;
  Object.defineProperty(global, 'navigator', { value: { userAgent: 'node.js' }, writable: false, configurable: true });
  global.localStorage = dom.window.localStorage || (function(){
    let store = {};
    return {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
      removeItem: (k) => { delete store[k]; },
      clear: () => { store = {}; },
    };
  })();

  // Render ToastProvider
  render(
    React.createElement(
      ToastProvider,
      null,
      React.createElement('div', null, 'root')
    )
  );

  // Dispatch event (act로 감싸기)
  await act(async () => {
    window.dispatchEvent(new window.CustomEvent('app:notification', { detail: { message: 'X', type: 'info' } }));
  });

  // Wait for toast
  try {
    await waitFor(() => screen.getByText('X'), { timeout: 2500 });
  } catch (e) {
    // body 전체 출력하여 실제 렌더링 여부 확인
    console.log('BODY:', document.body.innerHTML);
    throw e;
  }

  // Dispatch duplicate quickly (act로 감싸기)
  await act(async () => {
    window.dispatchEvent(new window.CustomEvent('app:notification', { detail: { message: 'X', type: 'info' } }));
  });
  await act(async () => {
    jest.advanceTimersByTime(500);
  });
  let nodes = document.querySelectorAll('[data-testid="toast"]');
  let count = Array.from(nodes).filter(n => n.textContent && n.textContent.includes('X')).length;
  expect(count).toBeLessThanOrEqual(1);

  // 3.5초 이상 대기 후 토스트가 사라지는지 확인 (타이머 강제 실행)
  await act(async () => {
    jest.advanceTimersByTime(3600);
    jest.runAllTimers();
  });
  nodes = document.querySelectorAll('[data-testid="toast"]');
  count = Array.from(nodes).filter(n => n.textContent && n.textContent.includes('X')).length;
  expect(count).toBe(0);

  // After 2s dispatch again
  await new Promise((r) => setTimeout(r, 1600));
  await act(async () => {
    window.dispatchEvent(new window.CustomEvent('app:notification', { detail: { message: 'X', type: 'info' } }));
  });
  await new Promise((r) => setTimeout(r, 200));
  const count2 = Array.from(document.querySelectorAll('div')).filter(n => n.textContent && n.textContent.includes('X')).length;
  expect(count2).toBeGreaterThanOrEqual(1);
}, 15000);
