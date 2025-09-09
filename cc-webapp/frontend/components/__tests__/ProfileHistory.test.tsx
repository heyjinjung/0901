// @ts-nocheck

import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react';

// mock unifiedApi used by the component (use alias path to match component import)
jest.mock('@/lib/unifiedApi', () => ({
  api: {
    get: jest.fn(),
  },
}));

import { api } from '@/lib/unifiedApi';
import ProfileHistory from '../ProfileHistory';

describe('ProfileHistory', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('loads and displays transactions when "더 불러오기" clicked', async () => {
  const sample = [
      {
        product_id: 1,
        amount: 100,
        status: 'ok',
        receipt_code: 'r1',
        created_at: new Date().toISOString(),
      },
    ];

  // return either array or object shape; component supports both
    api.get.mockImplementationOnce(async () => {
      await Promise.resolve(); // ensure microtask
      return { transactions: sample };
    });

    render(<ProfileHistory />);

    const loadBtn = screen.getByText(/더 불러오기/);
  await act(async () => { fireEvent.click(loadBtn); });

  // unifiedApi 호출이 수행되는지 확인
  await waitFor(() => expect(api.get).toHaveBeenCalled());
  // flush state updates
  await act(async () => { await Promise.resolve(); await Promise.resolve(); });
  // 로딩이 해제되어 버튼이 활성화될 때까지 대기
  await waitFor(() => expect(screen.getByRole('button', { name: '더 불러오기' })).toBeEnabled());
  // 리스트 아이템이 렌더링될 때까지 대기 후 내용 검증
  const items = await screen.findAllByRole('listitem');
  expect(items.length).toBeGreaterThan(0);
  expect(items[0].textContent || '').toMatch(/제품:\s*1/);
  expect(items[0].textContent || '').toMatch(/금액:\s*100/);
  });
});
// end of file
