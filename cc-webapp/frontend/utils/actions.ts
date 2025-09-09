import apiRequest from './api';

export type ActionPayload = {
  user_id: number;
  action_type: string;
  context?: Record<string, any>;
};

export async function postAction(payload: ActionPayload) {
  return await apiRequest('/api/actions', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function postActionsBatch(payloads: ActionPayload[]) {
  // Backend expects POST /api/actions/bulk with { items: [...] }
  try {
    return await apiRequest('/api/actions/bulk', {
      method: 'POST',
      body: JSON.stringify({ items: payloads })
    });
  } catch (err) {
    // Fallback: if bulk is unavailable, degrade to sequential single posts
    try {
      const results = [] as any[];
      for (const p of payloads) {
        results.push(await postAction(p));
      }
      return { logged: results.length };
    } catch (_) {
      throw err;
    }
  }
}

export type ShopBuyPayload = {
  user_id: number;
  product_id: string;
  amount: number; // price in gems/tokens
  quantity?: number;
  metadata?: Record<string, any>;
};

export async function buyProduct(payload: ShopBuyPayload & { idempotency_key?: string }) {
  // Unified purchase 엔드포인트로 전환: 서버는 product_id 와 (선택) idempotency_key만 필요
  const { product_id } = payload;
  const body = {
    product_id,
    idempotency_key: payload.idempotency_key || undefined,
  };
  return await apiRequest('/api/shop/purchase', {
    method: 'POST',
    body: JSON.stringify(body)
  });
}
