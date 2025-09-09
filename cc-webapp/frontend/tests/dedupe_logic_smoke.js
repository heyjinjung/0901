// Lightweight smoke test that replicates NotificationToast dedupe logic
(async () => {
  const last = { key: null, at: 0 };
  function push(message, type) {
    const key = `${type ?? 'info'}:${message}`;
    const now = Date.now();
    if (last.key === key && now - last.at < 1500) return false; // suppressed
    last.key = key;
    last.at = now;
    return true; // shown
  }

  const r1 = push('E2E TEST', 'info');
  const r2 = push('E2E TEST', 'info');
  await new Promise((r) => setTimeout(r, 1600));
  const r3 = push('E2E TEST', 'info');

  console.log('results:', { r1, r2, r3 });
  if (r1 !== true || r2 !== false || r3 !== true) {
    console.error('FAIL: dedupe logic did not behave as expected');
    process.exitCode = 2;
    return;
  }
  console.log('PASS: dedupe logic behaves as expected (show, suppress, show)');
})();
