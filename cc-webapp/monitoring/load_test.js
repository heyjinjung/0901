// cc-webapp/monitoring/load_test.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// --- Configuration ---
// These should point to your staging or test environment.
// Ensure the environment can handle the load.
const BASE_URL_BACKEND = `${__ENV.TARGET_BACKEND_URL || 'http://staging.cc-webapp.com/api'}`;
const BASE_URL_FRONTEND = `${__ENV.TARGET_FRONTEND_URL || 'http://staging.cc-webapp.com'}`;

// Custom Metrics to track specific endpoint performance and error rates
const actionsLatency = new Trend('actions_latency', true); // true indicates it's a time metric
const gachaPullLatency = new Trend('gacha_pull_latency', true);
const slotsPageLatency = new Trend('slots_page_latency', true);
const errorRate = new Rate('errors'); // Tracks the rate of failed checks

// Counters for specific actions
const actionsCount = new Counter('actions_total_requests');
const gachaPullCount = new Counter('gacha_pulls_total_requests');
const slotsPageRequestsCount = new Counter('slots_page_total_requests');

// --- Test Options ---
// Defines the shape of the load test (stages, VUs, duration, thresholds)
export const options = {
  stages: [
    { duration: '30s', target: 50 },   // Ramp up to 50 Virtual Users over 30 seconds
    { duration: '1m', target: 100 },  // Ramp up to 100 VUs over the next 1 minute
    { duration: '2m', target: 100 },  // Stay at 100 VUs for 2 minutes (steady state)
    // { duration: '30s', target: 200 }, // Optional: further ramp up to 200 VUs
    // { duration: '1m', target: 200 },  // Optional: stay at 200 VUs
    { duration: '30s', target: 0 },    // Ramp down to 0 VUs
  ],
  thresholds: {
    // Global thresholds
    'http_req_duration': ['p(95)<300'],       // 95% of all HTTP requests should be below 300ms
    'http_req_failed': ['rate<0.02'],         // Global HTTP error rate should be less than 2%

    // Custom metric thresholds (latency for specific endpoints)
    'actions_latency': ['p(95)<200'],         // 95th percentile for POST /actions should be <200ms
  'gacha_pull_latency': ['p(95)<250'],      // 95th percentile for POST /api/games/gacha/pull should be <250ms
    'slots_page_latency': ['p(95)<500'],      // 95th percentile for GET /slots page load should be <500ms

    // Error rate for custom checks (if any specific checks fail beyond HTTP errors)
    'errors': ['rate<0.01'],                  // Custom error rate (e.g., failed content checks) <1%

    // Thresholds on checks
    'checks': ['rate>0.98'], // More than 98% of checks should pass
  },
  // Optional: k6 Cloud configuration
  ext: {
    loadimpact: {
      // projectID: 123456, // Your k6 Cloud Project ID
      // name: "CC Webapp - Staging Environment Load Test" // Test run name
      // distribution: { // Example for distributed load
      //   "amazon:us:ashburn": { loadZone: "amazon:us:ashburn", percent: 100 },
      // },
    }
  },
  // Optional: Define user agent
  // userAgent: "MyK6LoadTest/1.0",
};

// --- Helper Functions ---
function generateRandomActionPayload() {
  const actionTypes = ["GAME_START", "SPIN_SLOT", "PLAY_RPS", "VIEW_CONTENT", "DAILY_CHECKIN"];
  const userId = Math.floor(Math.random() * 10000) + 1; // Simulate up to 10,000 users
  return JSON.stringify({
    user_id: userId,
    action_type: actionTypes[Math.floor(Math.random() * actionTypes.length)],
    metadata: { source: "k6_load_test", value: Math.random() * 100, session_id: __VU }, // __VU is virtual user ID
    timestamp: new Date().toISOString(),
  });
}

function generateGachaPullPayload() {
  // Unified games router expects optional pullCount; auth is required in real env
  return JSON.stringify({ pullCount: 1 });
}

// --- Test Scenarios (default function executed by VUs) ---
export default function () {
  // Group for Backend API tests
  group('Backend API Load', function () {
    // Scenario 1: POST /api/actions
    const actionsPayload = generateRandomActionPayload();
    const actionsParams = {
      headers: { 'Content-Type': 'application/json', 'User-Agent': 'k6LoadTest' },
      tags: { endpoint_name: 'PostActions' }, // Tag for better filtering in results
    };
    const actionsRes = http.post(`${BASE_URL_BACKEND}/actions`, actionsPayload, actionsParams);

    const actionsCheck = check(actionsRes, {
      'POST /actions status is 200 or 201': (r) => r.status === 200 || r.status === 201,
    });
    if (!actionsCheck) { errorRate.add(1); } // Add to custom error rate if check fails
    actionsLatency.add(actionsRes.timings.duration);
    actionsCount.add(1);

    sleep(Math.random() * 1.5 + 0.5); // Think time: 0.5 to 2 seconds

    // Scenario 2: POST /api/games/gacha/pull (unified games router)
    const gachaPayload = generateGachaPullPayload();
    const gachaParams = {
      headers: { 'Content-Type': 'application/json', 'User-Agent': 'k6LoadTest' },
      tags: { endpoint_name: 'PostGachaPull' },
    };
    const gachaRes = http.post(`${BASE_URL_BACKEND}/games/gacha/pull`, gachaPayload, gachaParams);

    const gachaCheck = check(gachaRes, {
      'POST /api/games/gacha/pull status is 200': (r) => r.status === 200,
      'POST /api/games/gacha/pull response contains items': (r) => Array.isArray(r.json('items') || []),
    });
    if (!gachaCheck) { errorRate.add(1); }
    gachaPullLatency.add(gachaRes.timings.duration);
    gachaPullCount.add(1);
  });

  sleep(Math.random() * 2 + 1); // Think time: 1 to 3 seconds

  // Group for Frontend Page Load tests
  group('Frontend Page Load', function () {
    // Scenario 3: GET /slots (Frontend Page)
    // This primarily tests server response time for the HTML and potentially initial client-side assets.
    // It does not measure client-side rendering performance or user interactions.
    const slotsPageParams = {
        headers: { 'User-Agent': 'k6LoadTest' },
        tags: { page_name: 'SlotsPage' },
    };
    const slotsRes = http.get(`${BASE_URL_FRONTEND}/slots`, slotsPageParams);

    const slotsCheck = check(slotsRes, {
      'GET /slots page status is 200': (r) => r.status === 200,
      'GET /slots page body contains "Slot Machine"': (r) => r.body.includes('Slot Machine'), // Basic content check
    });
    if (!slotsCheck) { errorRate.add(1); }
    slotsPageLatency.add(slotsRes.timings.duration);
    slotsPageRequestsCount.add(1);
  });

  sleep(Math.random() * 2.5 + 1.5); // Think time: 1.5 to 4 seconds before next VU iteration
}

// Optional: Teardown function for any cleanup after the test run
// export function teardown(data) {
//   console.log('Load test finished.');
//   // console.log(JSON.stringify(data)); // data contains aggregated metrics
// }

// How to run:
// 1. Install k6: https://k6.io/docs/getting-started/installation/
// 2. Run the test: k6 run cc-webapp/monitoring/load_test.js
//    Or with environment variables for base URLs:
//    k6 run -e TARGET_BACKEND_URL="http://your-staging-backend-url/api" -e TARGET_FRONTEND_URL="http://your-staging-frontend-url" cc-webapp/monitoring/load_test.js
//
// To run in k6 Cloud:
// k6 cloud cc-webapp/monitoring/load_test.js
// (after logging in with `k6 login cloud`)
