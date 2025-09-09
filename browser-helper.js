// 브라우저 개발자 도구에서 실행할 로그인 헬퍼
window.quickLogin = async function() {
  console.log('🔐 Quick Login 시작...');
  
  try {
    // 1. 로그인 API 호출
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
    
    if (!response.ok) {
      throw new Error(`Login failed: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ 로그인 성공:', data);
    
    // 2. 토큰을 localStorage에 저장
    const tokens = {
      access_token: data.access_token,
      refresh_token: data.refresh_token || data.access_token
    };
    
    localStorage.setItem('cc_auth_tokens', JSON.stringify(tokens));
    console.log('💾 토큰 저장 완료');
    
    // 3. 즉시 프로필 API 테스트
    const profileResponse = await fetch('http://localhost:8000/api/users/profile', {
      headers: {
        'Authorization': `Bearer ${data.access_token}`,
        'Accept': 'application/json'
      }
    });
    
    if (profileResponse.ok) {
      const profileData = await profileResponse.json();
      console.log('👤 프로필 데이터:', profileData);
    }
    
    console.log('🎉 Quick Login 완료! 이제 프로필 페이지를 새로고침하세요.');
    return true;
    
  } catch (error) {
    console.error('❌ Quick Login 실패:', error);
    return false;
  }
};

window.checkTokens = function() {
  const tokens = localStorage.getItem('cc_auth_tokens');
  console.log('🔍 현재 저장된 토큰:', tokens ? JSON.parse(tokens) : '없음');
};

window.clearTokens = function() {
  localStorage.removeItem('cc_auth_tokens');
  localStorage.removeItem('cc_access_token');
  localStorage.removeItem('cc_access_exp');
  console.log('🗑️ 모든 토큰 삭제됨');
};

console.log('🚀 헬퍼 함수가 로드되었습니다:');
console.log('- quickLogin(): 자동 로그인 실행');
console.log('- checkTokens(): 저장된 토큰 확인');
console.log('- clearTokens(): 모든 토큰 삭제');
console.log('사용법: 개발자 도구에서 quickLogin() 실행 후 프로필 페이지 새로고침');
