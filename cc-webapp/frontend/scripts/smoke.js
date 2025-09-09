let fetchFn = global.fetch;
try {
  if (!fetchFn) {
    // Try optional node-fetch if installed
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    fetchFn = require('node-fetch');
  }
} catch (_) {
  // leave fetchFn undefined
}

if (!fetchFn) {
  console.error('No fetch available (install node-fetch for Node<18 or run on Node 18+)');
  process.exit(2);
}

async function check(url) {
  try {
    const res = await fetchFn(url, { method: 'GET' });
    console.log(`${url} -> ${res.status}`);
    return res.ok;
  } catch (err) {
    console.error(`${url} -> ERROR`, err.message || err);
    return false;
  }
}

async function main() {
  const backend = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
  const frontend = process.env.FRONTEND_URL || 'http://127.0.0.1:3000';

  const endpoints = [
    `${backend.replace(/\/$/, '')}/health`
  ];

  let ok = true;
  for (const e of endpoints) {
    const r = await check(e);
    ok = ok && r;
  }

  if (!ok) process.exit(2);
  console.log('Smoke checks passed');
}

main();
