#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

function log(msg) { console.log(`[openapi-drift] ${msg}`); }

const apiBase = process.env.API_BASE_URL || process.env.OPENAPI_BASE_URL || '';
if (!apiBase) {
    log('API_BASE_URL not set; skipping drift check.');
    process.exit(0);
}

const frontendDir = process.cwd();
const specPath = path.join(frontendDir, 'openapi_spec.json');
const livePath = path.join(frontendDir, 'temp_openapi_live.json');

const fetchJson = async (url) => {
    const res = await fetch(url, { headers: { accept: 'application/json' } });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return await res.json();
};

const stableStringify = (obj) => JSON.stringify(obj, Object.keys(obj).sort(), 2);

(async () => {
    try {
        log(`Fetching ${apiBase}/api/openapi.json`);
        const live = await fetchJson(`${apiBase}/api/openapi.json`);
        fs.writeFileSync(livePath, JSON.stringify(live, null, 2));

        const committed = JSON.parse(fs.readFileSync(specPath, 'utf8'));
        const a = stableStringify(committed);
        const b = stableStringify(live);

        if (a !== b) {
            log('DRIFT DETECTED between openapi_spec.json and live spec.');
            log('Save diff locally or update openapi_spec.json.');
            process.exit(2);
        }
        log('No drift detected.');
    } catch (err) {
        console.error('[openapi-drift] error:', err.message || err);
        process.exit(1);
    }
})();
