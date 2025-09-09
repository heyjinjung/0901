# 🎯 Tailwind CSS V4 IDE 호환성 가이드

## ⚠️ 중요: Tailwind V4 환경에서의 주의사항

### 🔧 1. IDE 설정 필수 조정

#### **VS Code 설정**
```json
// .vscode/settings.json
{
  "tailwindCSS.experimental.configFile": null,
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["cx\\(([^)]*)\\)", "(?:'|\"|`)([^']*)(?:'|\"|`)"],
    ["cn\\(([^)]*)\\)", "(?:'|\"|`)([^']*)(?:'|\"|`)"]
  ],
  "tailwindCSS.files.exclude": [
    "**/.git/**",
    "**/node_modules/**",
    "**/.hg/**",
    "**/.svn/**"
  ],
  "css.validate": false,
  "postcss.validate": false
}
```

#### **WebStorm/IntelliJ 설정**
- **File > Settings > Languages & Frameworks > Style Sheets > Tailwind CSS**
- **Configuration file path**: 비워두기 (V4는 config 파일 불필요)
- **PostCSS configuration**: `styles/globals.css` 지정

### 🚫 2. 절대 하지 말아야 할 것들

#### **❌ tailwind.config.js 파일 생성 금지**
```javascript
// ❌ 절대 생성하지 마세요!
module.exports = {
  // V4에서는 이 파일이 충돌을 일으킵니다
}
```

#### **❌ 구 버전 임포트 문법 사용 금지**
```tsx
// ❌ 구 버전 문법
import { Button } from '@/components/ui/button'
import clsx from 'clsx'

// ✅ V4 호환 문법
import { Button } from './components/ui/button'
import { cn } from './components/ui/utils'
```

#### **❌ CSS 변수 직접 조작 금지**
```css
/* ❌ 이렇게 하지 마세요 */
:root {
  --tw-bg-primary: #000;
}

/* ✅ globals.css에서 정의된 것만 사용 */
:root {
  --primary: #e6005e;
}
```

### ✅ 3. 반드시 지켜야 할 규칙들

#### **📁 파일 구조 규칙**
```
📁 프로젝트/
├── styles/
│   └── globals.css          # ✅ 메인 스타일 파일
├── components/ui/
│   ├── utils.ts            # ✅ cn 함수 정의
│   └── *.tsx              # ✅ UI 컴포넌트들
└── 절대 생성하지 말 것:
    ├── tailwind.config.js   # ❌ 금지!
    ├── tailwind.config.ts   # ❌ 금지!
    └── postcss.config.js    # ❌ 금지!
```

#### **🎨 CSS 커스텀 변수 사용법**
```css
/* ✅ globals.css에서만 정의 */
:root {
  --primary: #e6005e;
  --background: #0a0a0f;
}

@theme inline {
  --color-primary: var(--primary);
  --color-background: var(--background);
}
```

#### **📝 클래스명 작성 규칙**
```tsx
// ✅ 올바른 방법
<div className="bg-primary text-primary-foreground">

// ✅ 커스텀 CSS 변수 사용
<div className="bg-[var(--primary)]">

// ❌ 직접 색상값 사용 (IDE에서 인식 안됨)
<div className="bg-[#e6005e]">
```

### 🔧 4. IDE별 트러블슈팅

#### **VS Code 문제 해결**
```bash
# 1. Tailwind CSS IntelliSense 확장 재설치
# 2. TypeScript 서버 재시작: Ctrl+Shift+P > "TypeScript: Restart TS Server"
# 3. 워크스페이스 다시 로드: Ctrl+Shift+P > "Developer: Reload Window"
```

#### **WebStorm 문제 해결**
```bash
# 1. 캐시 삭제: File > Invalidate Caches and Restart
# 2. Tailwind CSS 플러그인 활성화 확인
# 3. PostCSS 지원 활성화: Settings > PostCSS
```

#### **Cursor/Sublime Text 문제 해결**
```bash
# 1. CSS 파일 연결 확인
# 2. LSP 서버 재시작
# 3. 프로젝트 재인덱싱
```

### 🚨 5. 자주 발생하는 오류들

#### **오류 1: "Unknown at rule @theme"**
```css
/* ❌ 문제 상황 */
@theme {
  /* CSS가 인식되지 않음 */
}

/* ✅ 해결책 */
@theme inline {
  /* inline 키워드 추가 */
}
```

#### **오류 2: "Class name not found"**
```tsx
// ❌ 문제 상황
<div className="bg-primary-500">

// ✅ 해결책 - 정의된 변수만 사용
<div className="bg-primary">
```

#### **오류 3: "CSS 변수 인식 안됨"**
```css
/* ✅ globals.css에서 올바른 정의 */
:root {
  --primary: #e6005e;
}

@theme inline {
  --color-primary: var(--primary);
}
```

### 📋 6. 체크리스트

#### **프로젝트 설정 체크**
- [ ] `tailwind.config.js` 파일이 없는지 확인
- [ ] `styles/globals.css`에 `@theme inline` 사용
- [ ] `components/ui/utils.ts`에 `cn` 함수 정의
- [ ] 모든 import에서 `@버전` 제거

#### **IDE 설정 체크**
- [ ] Tailwind CSS 확장/플러그인 최신 버전
- [ ] CSS 검증 비활성화
- [ ] PostCSS 검증 비활성화
- [ ] TypeScript 서버 재시작

#### **코드 작성 체크**
- [ ] 모든 색상은 CSS 변수로 정의
- [ ] `cn()` 함수로 클래스명 조합
- [ ] 커스텀 효과는 `@layer utilities`에 정의
- [ ] 애니메이션은 `@keyframes`로 정의

### 🎯 7. 권장 워크플로우

#### **새 컴포넌트 생성 시**
1. `components/ui/` 폴더에 생성
2. `forwardRef` 패턴 사용
3. `cn()` 함수로 클래스명 조합
4. 커스텀 스타일은 `globals.css`에 정의

#### **스타일 수정 시**
1. 기존 CSS 변수 확인
2. 필요시 `globals.css`에 새 변수 추가
3. `@theme inline`에 Tailwind 매핑 추가
4. 컴포넌트에서 변수명으로 사용

#### **배포 전 체크**
1. IDE에서 CSS 오류 없는지 확인
2. 브라우저에서 스타일 정상 적용 확인
3. 다크모드 정상 동작 확인
4. 반응형 디자인 정상 동작 확인

## 🎮 게임 프로젝트 특화 주의사항

### **Glass Metal 효과 사용법**
```tsx
// ✅ 올바른 사용법
<div className="glass-metal glass-metal-hover">
  {/* 내용 */}
</div>
```

### **그라데이션 텍스트 사용법**
```tsx
// ✅ 올바른 사용법
<h1 className="text-gradient-primary">
  게임 타이틀
</h1>
```

### **애니메이션 효과 사용법**
```tsx
// ✅ 올바른 사용법
<div className="btn-hover-lift metal-shine">
  버튼
</div>
```

---

**⚠️ 이 가이드를 반드시 팀 전체가 숙지하고 준수해야 합니다!**