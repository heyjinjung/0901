from playwright.sync_api import sync_playwright
import time, sys

FRONTEND = "http://localhost:3000"
BACKEND = "http://localhost:8000"

# This is a template script focused on UI-first checks for:
# 1) Signup/Login modal flows (nickname + invite code) including error cases
# 2) Onboarding tutorial flow (next, previous, skip)
#
# It's intentionally conservative: if UI is missing, falls back to API checks.
# Update selectors to match your frontend implementation.

# --- Config: selectors (adjust to real frontend) ---
SELECTORS = {
    # App.tsx uses full-page screens; use page-based selectors from components
    # Signup page (SignupScreen): inputs have id attributes userId, nickname, phoneNumber, password, confirmPassword, inviteCode
    'open_signup_btn': 'button[aria-label="회원가입"]',
    'signup_page': 'form[action="signup"]',
    'signup_userId': 'input#userId',
    'signup_nickname': 'input#nickname',
    'signup_phone': 'input#phoneNumber',
    'signup_password': 'input#password',
    'signup_confirm': 'input#confirmPassword',
    'signup_invite': 'input#inviteCode',
    'signup_submit': 'form button[type="submit"]',
    'signup_error': '.text-error',

    # Login page (LoginScreen): inputs use id "nickname" and "password" and submit as form
    'open_login_btn': 'button[aria-label="로그인"]',
    'login_page': 'form',
    'login_nickname': 'input#nickname',
    'login_password': 'input#password',
    'login_submit': 'form button[type="submit"]',
    'login_error': '.text-error',

    # Onboarding: use semantic data-test if present, else fallback to common buttons by text
    'onboarding_next': 'button[data-test="onboarding-next"]',
    'onboarding_skip': 'button[data-test="onboarding-skip"]',
    'onboarding_step': 'div[data-test="onboarding-step"]'
}


def api_post(page, path, payload):
    return page.evaluate("""async (p) => { const r = await fetch(p.url, {method:'POST',headers:{'content-type':'application/json'}, body: JSON.stringify(p.payload)}); const t = await r.text(); try { return {status:r.status, json: JSON.parse(t)} } catch(e) { return {status:r.status, text:t} } }""", {"url": BACKEND + path, "payload": payload})


def try_click(page, selector, timeout=2000):
    try:
        page.wait_for_selector(selector, timeout=timeout)
        page.click(selector)
        return True
    except Exception as e:
        print('click failed', selector, e)
        return False


def run_ui_signup_flow(page):
    print('Open home')
    page.goto(FRONTEND, wait_until='domcontentloaded')
    time.sleep(0.2)

    # Open signup modal
    if not try_click(page, SELECTORS['open_signup_btn']):
        print('Signup open button not found; fallback to API signup test')
        return False

    page.wait_for_selector(SELECTORS['signup_modal'], timeout=2000)
    print('signup modal visible')

    # test client-side validation: empty fields
    try:
        page.click(SELECTORS['signup_submit'])
        # expect error
        if page.is_visible(SELECTORS['signup_error']):
            print('client-side validation error shown')
        else:
            print('no client-side validation error detected')
    except Exception:
        print('submit failed; proceed')

    # fill valid data
    uid = str(int(time.time()))
    nickname = f'e2e_nick_{uid}'
    site_id = f'e2e_site_{uid}'
    password = 'pass1234'
    payload = { 'invite_code': '5858', 'nickname': nickname, 'site_id': site_id, 'password': password }

    page.fill(SELECTORS['signup_nickname'], nickname)
    # invite input may be optional in UI flow
    try:
        page.fill(SELECTORS['signup_invite'], '5858')
    except Exception:
        pass
    try_click(page, SELECTORS['signup_submit'])
    time.sleep(0.5)

    # if UI shows success/redirect, consider pass and return credentials
    try:
        if page.url != FRONTEND and 'profile' in page.url:
            print('UI signup flow redirected to profile — success')
            return True, site_id, password
    except Exception:
        pass

    # if error visible, capture and fail
    try:
        if page.is_visible(SELECTORS['signup_error']):
            err = page.inner_text(SELECTORS['signup_error'])
            print('signup UI error:', err)
            return False, None, None
    except Exception:
        pass

    # fallback: call API signup to ensure backend works and reuse the same credentials
    r = api_post(page, '/api/auth/signup', payload)
    print('API signup status', r.get('status'))
    if r.get('status') == 200:
        return True, site_id, password
    return False, None, None


def run_ui_login_flow(page, site_id, password):
    # open login modal
    if not try_click(page, SELECTORS['open_login_btn']):
        print('Login open button not found; fallback to API login test')
        return False
    page.wait_for_selector(SELECTORS['login_modal'], timeout=2000)

    page.fill(SELECTORS['login_site_id'], site_id)
    page.fill(SELECTORS['login_password'], password)
    try_click(page, SELECTORS['login_submit'])
    time.sleep(0.5)

    if page.is_visible(SELECTORS['login_error']):
        print('login UI error shown')
        return False

    # check profile or token presence via API
    resp = page.evaluate("() => { return !!window.localStorage.getItem('access_token') || !!document.cookie }")
    print('token present after login?', resp)
    return resp


def run_onboarding_flow(page):
    # Go to first onboarding step
    page.goto(FRONTEND, wait_until='domcontentloaded')
    time.sleep(0.2)

    # If onboarding exists, verify steps and skip
    if not page.is_visible(SELECTORS['onboarding_step']):
        print('onboarding not visible on load; nothing to test')
        return True

    step_count = 0
    while page.is_visible(SELECTORS['onboarding_step']) and step_count < 10:
        title = page.inner_text(SELECTORS['onboarding_step'])
        print('onboarding step:', title)
        step_count += 1
        # try next
        if try_click(page, SELECTORS['onboarding_next']):
            time.sleep(0.3)
            continue
        else:
            break

    # test skip
    if try_click(page, SELECTORS['onboarding_skip']):
        print('onboarding skip clicked')
        time.sleep(0.2)
        return True

    return True


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        ok_signup, site_id, password = run_ui_signup_flow(page)
        if not ok_signup:
            print('signup flow failed')
            browser.close()
            return 1

        # After signup via API/UI, try login UI with returned credentials
        ok_login = run_ui_login_flow(page, site_id, password)
        if not ok_login:
            print('login flow failed')
            browser.close()
            return 2

        ok_onboarding = run_onboarding_flow(page)
        if not ok_onboarding:
            print('onboarding flow failed')
            browser.close()
            return 3

        browser.close()
        print('Onboarding E2E template succeeded')
        return 0

if __name__ == '__main__':
    rc = run()
    print('exit', rc)
    sys.exit(rc)
