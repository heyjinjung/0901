// Dev API Logger - served from /devtools/dev_api_logger.js
// This file is copied from cc-webapp/devtools/dev_api_logger.js to be served by Next.js public/ during development.
(function(){
  if(window.__DEV_API_LOGGER_ACTIVE) { console.warn('Dev API Logger already active'); return; }
  window.__DEV_API_LOGGER_ACTIVE = true;
  window.__devApiLogs = window.__devApiLogs || {actions:[], requests:[]};

  function now(){ return Date.now(); }
  function selectorFor(el){ if(!el) return null; try{ if(el.id) return '#'+el.id; if(el.className) return el.tagName.toLowerCase()+'.'+String(el.className).split(' ').join('.'); return el.tagName.toLowerCase(); }catch(e){return el.tagName||null} }

  window.addEventListener('click', function(e){
    const a = { type:'click', time: now(), x: e.clientX, y: e.clientY, selector: selectorFor(e.target), text: (e.target && e.target.innerText)?String(e.target.innerText).slice(0,120):null };
    window.__devApiLogs.actions.push(a);
    window.__devApiLogs.actions = window.__devApiLogs.actions.slice(-200);
    console.debug('[dev-api-logger] action', a);
  }, true);
  window.addEventListener('scroll', function(e){
    const a = { type:'scroll', time: now(), scrollY: window.scrollY, scrollX: window.scrollX };
    window.__devApiLogs.actions.push(a);
    window.__devApiLogs.actions = window.__devApiLogs.actions.slice(-200);
  }, true);

  function recentAction(maxAgeMs){
    const cutoff = now() - (maxAgeMs||2000);
    for(let i=window.__devApiLogs.actions.length-1;i>=0;i--){ if(window.__devApiLogs.actions[i].time>=cutoff) return window.__devApiLogs.actions[i]; }
    return null;
  }

  const _origFetch = window.fetch.bind(window);
  window.fetch = async function(input, init){
    const start = now();
    let method = (init && init.method) || (typeof input === 'string' ? 'GET' : (input && input.method)) || 'GET';
    let url = (typeof input === 'string') ? input : (input && input.url) || '';
    const reqBody = init && init.body ? init.body : null;
    const assocAction = recentAction(3000);
    const reqRecord = { kind:'fetch', time:start, method, url, requestBody: reqBody, action: assocAction };
    window.__devApiLogs.requests.push(reqRecord);
    try{
      const resp = await _origFetch(input, init);
      const cloned = resp.clone();
      let text = '';
      try{ text = await cloned.text(); }catch(e){ text = '<unreadable>'; }
      const duration = now()-start;
      Object.assign(reqRecord, { status: resp.status, ok: resp.ok, duration, responseText: text.slice(0,2000) });
      console.groupCollapsed(`[dev-api] ${method} ${url} -> ${resp.status} (${duration}ms)`);
      if(assocAction) console.log('action ->', assocAction);
      console.log('request ->', {method,url,requestBody:reqBody});
      console.log('response ->', {status:resp.status, ok:resp.ok, bodyPreview: reqRecord.responseText});
      console.groupEnd();
      return resp;
    }catch(err){
      const duration = now()-start;
      Object.assign(reqRecord, { error: String(err), duration });
      console.error('[dev-api] fetch error', method, url, err);
      throw err;
    }
  };

  (function(){
    const OldXHR = window.XMLHttpRequest;
    function NewXHR(){
      const xhr = new OldXHR();
      let _method = null, _url = null, _body = null, _start=null;
      const _open = xhr.open;
      xhr.open = function(method,url){ _method = method; _url = url; return _open.apply(this, arguments); };
      const _send = xhr.send;
      xhr.send = function(body){
        _body = body; _start = now();
        const assocAction = recentAction(3000);
        const rec = { kind:'xhr', time:_start, method:_method, url:_url, requestBody:_body, action:assocAction };
        window.__devApiLogs.requests.push(rec);
        this.addEventListener('load', function(){
          const duration = now()-_start;
          let respText = null; try{ respText = xhr.responseText; }catch(e){ respText = '<unreadable>'; }
          Object.assign(rec, { status: xhr.status, duration, responseText: (respText||'').slice(0,2000) });
          console.groupCollapsed(`[dev-api xhr] ${_method} ${_url} -> ${xhr.status} (${duration}ms)`);
          if(assocAction) console.log('action ->', assocAction);
          console.log('request ->', {method:_method,url:_url,requestBody:_body});
          console.log('response ->', {status:xhr.status, bodyPreview: rec.responseText});
          console.groupEnd();
        });
        this.addEventListener('error', function(){ const duration = now()-_start; Object.assign(rec,{error:'network', duration}); console.error('[dev-api xhr] error', _method,_url); });
        return _send.apply(this, arguments);
      };
      return xhr;
    }
    window.XMLHttpRequest = NewXHR;
  })();

  window.__devApiLogger = {
    dump: function(){ return JSON.parse(JSON.stringify(window.__devApiLogs)); },
    download: function(){ const data = 'data:application/json;charset=utf-8,'+encodeURIComponent(JSON.stringify(window.__devApiLogs)); const a=document.createElement('a'); a.href=data; a.download='dev_api_logs.json'; document.body.appendChild(a); a.click(); a.remove(); },
    stop: function(){ window.__DEV_API_LOGGER_ACTIVE=false; console.warn('Dev API Logger stopped; reload to fully restore originals'); }
  };

  console.info('Dev API Logger initialized. Use window.__devApiLogger.dump()/download() to inspect logs.');
})();
