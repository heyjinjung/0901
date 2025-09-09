# Casino-Club F2P 프론트엔드 로컬 개발 가이드

## 📋 개요
이 문서는 Docker 환경에서 Next.js 15.3.3 호환성 문제로 인해 로컬에서 프론트엔드 개발을 진행하는 방법을 안내합니다.

## 🚀 로컬 개발환경 설정

### 1. 필수 요구사항
```
- Node.js 18.17.0 이상 (20.x LTS 권장)
- npm 10.x 또는 yarn 1.22.x
- Git
- 코드 에디터 (VS Code 권장)
```

### 2. 프로젝트 설정
```bash
# 프로젝트 디렉토리로 이동
cd cc-webapp/frontend

# 의존성 설치
npm install
# 또는
yarn install
```

### 3. 로컬 개발 서버 실행
```bash
# 개발 서버 실행
npm run dev
# 또는
yarn dev
```

### 4. 모의 인증 시스템 설정 (백엔드 연결 전)
백엔드 인증 시스템이 완전히 구현되기 전에는 모의 응답으로 개발하는 것이 좋습니다:

```bash
# cc-webapp/frontend/src/mocks/handlers.js 파일 생성
mkdir -p src/mocks
touch src/mocks/handlers.js

# MSW(Mock Service Worker)를 사용한 모의 인증 응답 설정
npm install msw --save-dev
```

모의 핸들러 예시:
```javascript
// src/mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  // 회원가입 모의 응답
  rest.post('http://localhost:8000/api/auth/signup', (req, res, ctx) => {
    const { invite_code } = req.body;
    
    if (invite_code !== '5858') {
      return res(
        ctx.status(400),
        ctx.json({ detail: "유효하지 않은 초대코드입니다" })
      );
    }
    
    return res(
      ctx.status(200),
      ctx.json({
        access_token: "mock_token_123456",
        token_type: "bearer",
        user: {
          id: 1,
          site_id: req.body.site_id,
          nickname: req.body.nickname,
          phone_number: req.body.phone_number,
          is_active: true,
          is_admin: false,
          created_at: new Date().toISOString(),
          last_login: null
        }
      })
    );
  }),

  // 로그인 모의 응답
  rest.post('http://localhost:8000/api/auth/login', (req, res, ctx) => {
    const { site_id, password } = req.body;
    
    if (site_id === 'testuser123' && password === 'password123') {
      return res(
        ctx.status(200),
        ctx.json({
          access_token: "mock_token_123456",
          token_type: "bearer",
          user: {
            id: 1,
            site_id: "testuser123",
            nickname: "테스트유저",
            phone_number: "01012345678",
            is_active: true,
            is_admin: false,
            created_at: new Date().toISOString(),
            last_login: new Date().toISOString()
          }
        })
      );
    }
    
    return res(
      ctx.status(401),
      ctx.json({ detail: "아이디 또는 비밀번호가 올바르지 않습니다." })
    );
  })
];
```

## 🔌 로컬-Docker 연결 설정

### 1. API 엔드포인트 설정
`cc-webapp/frontend/.env.local` 파일을 생성하고 다음과 같이 설정:

```env
# Docker 백엔드 API 연결 설정
NEXT_PUBLIC_API_URL=http://localhost:8000

# 개발 모드 활성화 (옵션)
NEXT_PUBLIC_DEV_MODE=true

# 개발 중 인증 디버깅 (옵션, 주의: 프로덕션에서는 제거)
NEXT_PUBLIC_DEBUG_AUTH=true
```

> **참고**: 백엔드 서비스의 상태는 `http://localhost:8000/health` 엔드포인트로 확인할 수 있습니다.
> API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

### 2. CORS 설정 확인
Docker의 백엔드 환경에서 CORS 설정이 로컬 프론트엔드 서버(http://localhost:3000)를 허용하는지 확인:

```python
# 백엔드 CORS 설정 확인 (cc-webapp/backend/app/main.py)
origins = [
    "http://localhost:3000",  # 로컬 프론트엔드
    "http://localhost:8000",  # 백엔드
]
```

## 🧪 로컬-Docker 통합 테스트

### 1. API 연결 테스트
1. Docker 백엔드 서비스 실행 확인
```powershell
.\docker-manage.ps1 status
```

2. 로컬 프론트엔드에서 백엔드 API 연결 테스트
```bash
# 브라우저 개발자 도구 콘솔에서 확인
fetch('http://localhost:8000/health').then(res => res.json()).then(console.log)
```

3. 인증 시스템 현재 상태 요약 (2025-08-06 기준)
```
✅ 헬스체크 API: 정상 작동 (/health)
✅ API 문서: 정상 접근 가능 (/docs)
✅ 초대코드 검증: 기능 작동 중 (잘못된 코드 입력 시 400 에러)
❌ 회원가입: 서버 오류 발생 중 (500 에러)
❌ 일반 로그인: 서버 오류 발생 중 (500 에러)
❌ 어드민 로그인: 서버 오류 발생 중 (500 에러)
```

### 2. 인증 흐름 테스트
1. 로컬 프론트엔드에서 백엔드 로그인 API 호출
   ```bash
   # 브라우저 개발자 도구 콘솔에서 실행
   fetch('http://localhost:8000/api/auth/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ site_id: 'testuser123', password: 'password123' })
   }).then(res => res.json()).then(console.log).catch(err => console.error('Login error:', err))
   ```
2. JWT 토큰 저장 및 사용 검증
   ```bash
   # 로그인 후 토큰을 저장하고 API 요청에 사용
   let token;
   fetch('http://localhost:8000/api/auth/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ site_id: 'testuser123', password: 'password123' })
   })
   .then(res => res.json())
   .then(data => {
     token = data.access_token;
     // 저장된 토큰으로 인증이 필요한 API 호출
     return fetch('http://localhost:8000/api/users/profile', {
       headers: { 'Authorization': `Bearer ${token}` }
     });
   })
   .then(res => res.json())
   .then(console.log)
   .catch(err => console.error('Authentication flow error:', err))
   ```
3. 인증이 필요한 API 엔드포인트 접근 테스트

## ⚠️ 알려진 문제점 및 해결 방법

### 1. Next.js Docker 호환성 문제
**문제**: Next.js 15.3.3에서 lightningcss.linux-x64-musl.node 네이티브 모듈 호환성 문제
**원인**: Linux Alpine 기반 Docker 컨테이너에서 네이티브 의존성 문제
**현재 해결방법**: 로컬 개발 환경에서만 프론트엔드 개발 진행

### 2. 백엔드 인증 시스템 문제
**문제**: 인증 관련 API 호출 시 서버 내부 오류(500) 발생
**원인**: 데이터베이스 연결 문제 또는 백엔드 구현 미완료 상태일 가능성
**현재 해결방법**: 
- 백엔드 로그 확인: `.\docker-manage.ps1 logs backend`
- 데이터베이스 로그 확인: `.\docker-manage.ps1 logs postgres`
- 백엔드 개발팀에 문의하여 인증 시스템 상태 확인
**프론트엔드 개발 방향**:
- 모킹된 응답으로 UI 개발 진행
- 백엔드가 해결될 때까지 인증 디버깅 모드 활성화 (`NEXT_PUBLIC_DEBUG_AUTH=true`)

### 2. 가능한 장기적 해결책
1. **Next.js 버전 다운그레이드**: 13.x 또는 14.x LTS 버전으로 다운그레이드
2. **Docker 이미지 변경**: node:20-bullseye 등 다른 베이스 이미지 사용
3. **커스텀 Dockerfile**: 필요한 네이티브 의존성을 수동으로 설치하는 스크립트 추가
4. **Nextjs App Router 마이그레이션**: Pages Router에서 App Router로 마이그레이션 진행

## 📊 개발 작업흐름

### 1. 일일 개발 루틴
```bash
# 1. Docker 백엔드 서비스 시작
.\docker-manage.ps1 start --tools

# 2. 로컬 프론트엔드 개발 서버 실행
cd cc-webapp/frontend
npm run dev

# 3. API 변경사항 확인
# 백엔드 API 문서 확인: http://localhost:8000/docs
```

### 2. 빌드 및 테스트
```bash
# 프론트엔드 빌드
npm run build

# 타입 체크
npm run type-check

# 테스트 실행
npm run test
```

## 🔄 배포 전략

### 1. 로컬-Docker 혼합 개발 단계
- 백엔드, 데이터베이스, 기타 서비스: Docker 환경 사용
- 프론트엔드: 로컬 개발 환경 사용

### 2. 배포 준비 단계
- 프론트엔드 빌드 산출물 생성
- Docker 환경에 수동 배포 또는 CI/CD 파이프라인 구성

### 3. 장기적 해결 계획
- Next.js Docker 호환성 문제 해결
- 전체 환경 Docker 통합
- 자동화된 CI/CD 파이프라인 구축

## 🔍 문제 해결 및 지원

### 1. 일반적인 문제
- **API 연결 문제**: CORS 설정 및 네트워크 연결 확인
- **환경 변수 문제**: .env.local 파일 설정 확인
- **타입 에러**: 프론트엔드-백엔드 타입 정의 일치 여부 확인
- **인증 관련 오류**: 
  - "Registration processing error occurred" - 회원가입 처리 오류 (500 오류)
  - "Login processing error occurred" - 로그인 처리 오류 (500 오류)
  - "Admin login processing error occurred" - 관리자 로그인 오류 (500 오류)
  - "유효하지 않은 초대코드입니다" - 초대코드 검증은 작동함 (400 오류)
  - 이러한 오류가 발생할 경우 백엔드 로그 확인 필요 (docker-manage.ps1 logs backend)
  - 데이터베이스 연결 상태 확인 (docker-manage.ps1 logs postgres)

### 2. 도움받기
- 기술 문의: [팀 채널 링크]
- 문서 업데이트 요청: [이슈 트래커 링크]
