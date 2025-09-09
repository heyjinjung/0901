// 브라우저 콘솔에서 실행할 인증 상태 확인 스크립트
console.log('=== 프론트엔드 인증 상태 디버깅 ===');

// 1. localStorage 확인
const TOKEN_KEY = 'cc_auth_tokens';
const tokens = localStorage.getItem(TOKEN_KEY);
console.log('1. 저장된 토큰:', tokens ? JSON.parse(tokens) : null);

// 2. 환경 변수 확인 (클라이언트에서는 process.env가 제한적임)
console.log('2. 현재 URL:', window.location.href);
console.log('3. API Origin 추정:', window.location.port === '3001' ? 'http://localhost:8000' : window.location.origin);

// 3. 직접 API 호출 테스트
async function testDirectAPICall() {
  console.log('4. 직접 API 호출 테스트:');
  
  // 먼저 로그인 시도
  try {
    const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        site_id: 'test123',
        password: 'password123'
      })
    });
    
    console.log('- 로그인 응답 상태:', loginResponse.status);
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json();
      console.log('- 로그인 성공:', loginData);
      
      // 토큰을 localStorage에 저장
      localStorage.setItem(TOKEN_KEY, JSON.stringify({
        access_token: loginData.access_token,
        refresh_token: loginData.refresh_token || loginData.access_token
      }));
      
      // 프로필 API 호출
      const profileResponse = await fetch('http://localhost:8000/api/users/profile', {
        headers: {
          'Authorization': `Bearer ${loginData.access_token}`,
          'Accept': 'application/json'
        }
      });
      
      console.log('- 프로필 응답 상태:', profileResponse.status);
      
      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        console.log('- 프로필 데이터:', profileData);
      } else {
        const errorText = await profileResponse.text();
        console.log('- 프로필 API 오류:', errorText);
      }
    } else {
      const errorText = await loginResponse.text();
      console.log('- 로그인 실패:', errorText);
    }
  } catch (error) {
    console.error('- API 호출 오류:', error);
  }
}

// 4. 프로필 화면으로 이동 테스트
function goToProfile() {
  console.log('5. 프로필 화면으로 이동...');
  // BottomNavigation에서 프로필 버튼 클릭 시뮬레이션
  const profileButton = document.querySelector('[data-testid="nav-profile"], button:contains("프로필")');
  if (profileButton) {
    profileButton.click();
  } else {
    console.log('- 프로필 버튼을 찾을 수 없습니다.');
  }
}

// 실행
testDirectAPICall();
console.log('=== 테스트 완료. 프로필로 이동하려면 goToProfile() 함수를 호출하세요 ===');
