// 크래시 게임 API 테스트
const API_BASE = 'http://localhost:8000';

async function testCrashGameAPI() {
    console.log('=== 크래시 게임 API 테스트 시작 ===');
    
    try {
        // 1. 로그인
        console.log('\n1. 로그인 중...');
        const loginResponse = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                site_id: 'admin',
                password: '123456'
            })
        });
        
        const loginData = await loginResponse.json();
        console.log('로그인 응답:', loginResponse.status, loginData);
        
        if (!loginResponse.ok) {
            throw new Error(`로그인 실패: ${loginData.detail}`);
        }
        
        const token = loginData.access_token;
        console.log('토큰 획득 성공:', token.substring(0, 20) + '...');
        
        // 2. 크래시 베팅
        console.log('\n2. 크래시 베팅 중...');
        const betResponse = await fetch(`${API_BASE}/api/games/crash/bet`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                bet_amount: 100,
                target_multiplier: 2.0
            })
        });
        
        const betData = await betResponse.json();
        console.log('베팅 응답:', betResponse.status, betData);
        
        if (!betResponse.ok) {
            throw new Error(`베팅 실패: ${betData.detail}`);
        }
        
        const sessionId = betData.session_id;
        console.log('베팅 성공! 세션 ID:', sessionId);
        console.log('실제 배수:', betData.actual_multiplier);
        console.log('결과:', betData.result);
        console.log('승리 여부:', betData.is_win);
        
        // 3. 수동 캐시아웃 테스트 (새로운 베팅)
        console.log('\n3. 수동 캐시아웃 테스트를 위한 새 베팅...');
        const bet2Response = await fetch(`${API_BASE}/api/games/crash/bet`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                bet_amount: 50,
                target_multiplier: 5.0  // 높은 목표로 설정
            })
        });
        
        const bet2Data = await bet2Response.json();
        console.log('두번째 베팅 응답:', bet2Response.status, bet2Data);
        
        if (bet2Response.ok && bet2Data.result === 'pending') {
            console.log('진행 중인 게임 감지! 수동 캐시아웃 시도...');
            
            // 4. 수동 캐시아웃
            const cashoutResponse = await fetch(`${API_BASE}/api/games/crash/cashout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    session_id: bet2Data.session_id,
                    cashout_multiplier: 1.5
                })
            });
            
            const cashoutData = await cashoutResponse.json();
            console.log('캐시아웃 응답:', cashoutResponse.status, cashoutData);
            
            if (cashoutResponse.ok) {
                console.log('수동 캐시아웃 성공!');
                console.log('캐시아웃 배수:', cashoutData.cashout_multiplier);
                console.log('획득 금액:', cashoutData.payout);
            }
        }
        
        // 5. 사용자 잔액 확인
        console.log('\n5. 최종 잔액 확인...');
        const profileResponse = await fetch(`${API_BASE}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const profileData = await profileResponse.json();
        console.log('프로필 응답:', profileResponse.status);
        if (profileResponse.ok) {
            console.log('현재 잔액:', profileData.gold_balance);
        }
        
        console.log('\n=== 크래시 게임 API 테스트 완료 ===');
        
    } catch (error) {
        console.error('테스트 실패:', error.message);
    }
}

// 테스트 실행
testCrashGameAPI();
