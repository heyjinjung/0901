// 브라우저 콘솔에서 실행할 인증 디버깅 스크립트

console.log('=== 토큰 디버깅 시작 ===');

// 1. localStorage의 토큰 상태 확인
const TOKEN_KEY = 'cc_auth_tokens';
const LEGACY_ACCESS_KEY = 'cc_access_token';

console.log('1. 토큰 스토리지 상태:');
const tokenBundle = localStorage.getItem(TOKEN_KEY);
const legacyToken = localStorage.getItem(LEGACY_ACCESS_KEY);

console.log('- 통합 번들:', tokenBundle ? JSON.parse(tokenBundle) : null);
console.log('- 레거시 토큰:', legacyToken);

// 2. 토큰 검증 (만료 여부)
if (tokenBundle) {
  try {
    const tokens = JSON.parse(tokenBundle);
    if (tokens.access_token) {
      const payload = JSON.parse(atob(tokens.access_token.split('.')[1]));
      const now = Math.floor(Date.now() / 1000);
      const expired = payload.exp <= now;
      console.log('2. 토큰 상태:');
      console.log('- 발급일:', new Date(payload.iat * 1000));
      console.log('- 만료일:', new Date(payload.exp * 1000));
      console.log('- 현재 시간:', new Date());
      console.log('- 만료 여부:', expired);
      console.log('- 사용자 ID:', payload.sub);
    }
  } catch (e) {
    console.error('토큰 파싱 오류:', e);
  }
}

// 3. 프로필 API 직접 호출 테스트
async function testProfileAPI() {
  console.log('3. 프로필 API 직접 호출 테스트:');
  
  const tokens = tokenBundle ? JSON.parse(tokenBundle) : null;
  if (!tokens?.access_token) {
    console.log('- 토큰이 없어서 테스트 불가');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:8000/api/users/profile', {
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Accept': 'application/json'
      }
    });
    
    console.log('- 응답 상태:', response.status);
    console.log('- 응답 헤더:', [...response.headers.entries()]);
    
    if (response.ok) {
      const data = await response.json();
      console.log('- 프로필 데이터:', data);
    } else {
      const error = await response.text();
      console.log('- 오류 응답:', error);
    }
  } catch (e) {
    console.error('- API 호출 오류:', e);
  }
}

// 4. 테스트 로그인 실행
async function testLogin() {
  console.log('4. 테스트 로그인 시도:');
  
  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        site_id: 'test123',
        password: 'password123'
      })
    });
    
    console.log('- 로그인 응답 상태:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('- 로그인 성공:', data);
      
      // 토큰 저장
      const newTokens = {
        access_token: data.access_token,
        refresh_token: data.refresh_token || data.access_token
      };
      localStorage.setItem(TOKEN_KEY, JSON.stringify(newTokens));
      console.log('- 새 토큰 저장됨');
    } else {
      const error = await response.text();
      console.log('- 로그인 실패:', error);
    }
  } catch (e) {
    console.error('- 로그인 오류:', e);
  }
}

// 실행
testProfileAPI();
console.log('=== 프로필 API 테스트 완료 ===');
console.log('테스트 로그인을 원하면 testLogin() 함수를 실행하세요.');
