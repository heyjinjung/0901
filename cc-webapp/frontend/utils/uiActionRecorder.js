// uiActionRecorder.js
// 간단한 개발용 액션 레코더: 스크롤/클릭 이벤트를 기록하고 마지막 동작을 되돌리는 단일-스텝 undo 기능 제공합니다.

const actionHistory = [];
const MAX_HISTORY = 50;

function pushAction(action) {
  actionHistory.push({ ts: Date.now(), ...action });
  if (actionHistory.length > MAX_HISTORY) actionHistory.shift();
  // eslint-disable-next-line no-console
  console.log('[UIRecorder] action pushed', action);
}

export function initUiActionRecorder({ recordClicks = true, recordScroll = true } = {}) {
  if (recordClicks) {
    document.addEventListener('click', (ev) => {
      try {
        const target = ev.target && ev.target instanceof Element ? ev.target : null;
        const info = {
          type: 'click',
          x: ev.clientX,
          y: ev.clientY,
          tag: target ? target.tagName : null,
          id: target ? target.id : null,
          classes: target ? target.className : null,
          selector: target ? computeSelector(target) : null,
        };
        pushAction(info);
      } catch (e) {
        // eslint-disable-next-line no-console
        console.warn('[UIRecorder] click record failed', e);
      }
    }, { capture: true, passive: true });
  }

  if (recordScroll) {
    let lastY = window.scrollY || window.pageYOffset || 0;
    window.addEventListener('scroll', () => {
      try {
        const y = window.scrollY || window.pageYOffset || 0;
        // 기록은 큰 변화만
        if (Math.abs(y - lastY) > 20) {
          lastY = y;
          pushAction({ type: 'scroll', y });
        }
      } catch (e) {
        // eslint-disable-next-line no-console
        console.warn('[UIRecorder] scroll record failed', e);
      }
    }, { passive: true });
  }
}

function computeSelector(el) {
  if (!(el instanceof Element)) return null;
  let path = [];
  while (el && el.nodeType === Node.ELEMENT_NODE) {
    let selector = el.nodeName.toLowerCase();
    if (el.id) {
      selector += `#${el.id}`;
      path.unshift(selector);
      break;
    } else {
      let sib = el, nth = 1;
      while ((sib = sib.previousElementSibling)) nth++;
      selector += `:nth-child(${nth})`;
    }
    path.unshift(selector);
    el = el.parentElement;
  }
  return path.join(' > ');
}

export function undoLastAction() {
  const last = actionHistory.pop();
  if (!last) return false;
  try {
    if (last.type === 'scroll') {
      window.scrollTo({ top: last.y, behavior: 'smooth' });
      // eslint-disable-next-line no-console
      console.log('[UIRecorder] scroll undone to', last.y);
      return true;
    }
    if (last.type === 'click') {
      // 클릭은 보통 상태 변화를 수반하므로 보장된 undo는 어렵습니다.
      // 대신 클릭 대상에 포커스를 주어 사용자가 수동으로 복구할 수 있게 합니다.
      const el = document.querySelector(last.selector || '') || document.getElementById(last.id) || null;
      if (el && typeof el.focus === 'function') el.focus();
      // eslint-disable-next-line no-console
      console.log('[UIRecorder] triggered focus on click target', last.selector || last.id);
      return true;
    }
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn('[UIRecorder] undo failed', e);
    return false;
  }
  return false;
}

export function getActionHistory() {
  return actionHistory.slice();
}

export default {
  initUiActionRecorder,
  undoLastAction,
  getActionHistory,
};
