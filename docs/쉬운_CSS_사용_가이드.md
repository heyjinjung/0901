# 🎨 쉬운 CSS 사용 가이드 (고등학생용)

**바로 복사해서 붙여넣으면 되는 CSS 클래스들!**

---

## 📏 **간격 & 패딩 (복사해서 바로 사용)**

### 🎯 **기본 간격** (8px 단위)
```html
<!-- 패딩 (안쪽 여백) -->
<div class="p-2">패딩 16px</div>
<div class="p-4">패딩 32px</div>
<div class="p-6">패딩 48px</div>

<!-- 마진 (바깥쪽 여백) -->
<div class="m-2">마진 16px</div>
<div class="m-4">마진 32px</div>
<div class="m-6">마진 48px</div>

<!-- 세로 간격만 -->
<div class="py-4">위아래만 32px</div>
<div class="px-4">좌우만 32px</div>
```

### 📊 **간격 치트시트**
| 클래스 | 실제 크기 | 언제 사용? |
|--------|-----------|-----------|
| `p-1` | 8px | 아주 작은 여백 |
| `p-2` | 16px | 버튼 안쪽 |
| `p-4` | 32px | 카드 안쪽 |
| `p-6` | 48px | 섹션 구분 |
| `p-8` | 64px | 큰 섹션 |

---

## 🎲 **레이아웃 & 그리드**

### 📱 **카드 배치**
```html
<!-- 한 줄에 카드 3개 -->
<div class="grid grid-cols-3 gap-4">
  <div class="bg-slate-800 p-4 rounded-lg">카드 1</div>
  <div class="bg-slate-800 p-4 rounded-lg">카드 2</div>
  <div class="bg-slate-800 p-4 rounded-lg">카드 3</div>
</div>

<!-- 반응형: 모바일 1개, 태블릿 2개, 데스크톱 3개 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="bg-slate-800 p-4 rounded-lg">게임 카드</div>
  <div class="bg-slate-800 p-4 rounded-lg">게임 카드</div>
  <div class="bg-slate-800 p-4 rounded-lg">게임 카드</div>
</div>
```

### 📐 **세로 배치 (플렉스)**
```html
<!-- 세로로 나란히 -->
<div class="flex flex-col gap-4">
  <div class="bg-purple-600 p-4">제목</div>
  <div class="bg-slate-700 p-4">내용</div>
  <div class="bg-purple-600 p-4">버튼</div>
</div>

<!-- 가로로 나란히 -->
<div class="flex gap-4">
  <div class="bg-purple-600 p-4">왼쪽</div>
  <div class="bg-slate-700 p-4 flex-1">가운데 (넓게)</div>
  <div class="bg-purple-600 p-4">오른쪽</div>
</div>
```

2. **반응형 브레이크포인트**
   ```css
   sm: 640px   // 모바일
   md: 768px   // 태블릿
   lg: 1024px  // 작은 데스크톱
   xl: 1280px  // 큰 데스크톱
   2xl: 1536px // 초대형 화면
   ```

3. **여백 시스템**
   ```css
   --spacing-1: 8px
   --spacing-2: 16px
   --spacing-3: 24px
   --spacing-4: 32px
   --spacing-5: 40px
   --spacing-6: 48px
   ```

4. **컨테이너 크기**
   ```css
   sm: 640px
   md: 768px
   lg: 1024px
   xl: 1280px
   full: 100%
   ```

5. **z-index 레이어**
   ```css
   --z-background: 0
   --z-content: 10
   --z-header: 20
   --z-sidebar: 30
   --z-modal: 40
   --z-tooltip: 50
   ```
  <style jsx>{`
        /* 모바일: 반응형, 데스크탑: 고정 크기 + 중앙 정렬 */
        body {
          overflow-x: hidden;
        }
        
        .container {
          margin-left: auto;
          margin-right: auto;
        }
        
        /* 반응형 패딩 조정 */
        @media (min-width: 768px) {
          main {
            padding-top: calc(var(--app-header-height-desktop) + 1.5rem);
            padding-bottom: calc(var(--bottom-nav-height) + 2rem);
          }
        }
        
        @media (min-width: 1024px) {
          main {
            padding-top: calc(var(--app-header-height-desktop) + 2rem);
            padding-bottom: calc(var(--bottom-nav-height) + 2.5rem);
          }
        }
        
        /* 데스크탑에서만 고정 크기 + 중앙 정렬 */
        @media (min-width: 1200px) {
          body {
            width: 1200px;
            margin: 0 auto;
            background: var(--color-background-primary);
          }
          
          .container {
            width: 1200px !important;
            max-width: none !important;
            padding-left: 1rem;
            padding-right: 1rem;
          }
        }
        
        /* 모든 화면에서 버튼 중앙 정렬 강화 */
        .button-container {
          display: flex !important;
          justify-content: center !important;
          align-items: center !important;
          text-align: center !important;
        }
        
        /* 섹션 자체도 중앙 정렬 */
        section {
          text-align: center !important;
        }
        
        /* 모든 div에 중앙 정렬 강제 적용 */
        section div {
          justify-content: center !important;
          align-items: center !important;
---

## 🎨 **색상 (네온 테마)**

### 🌈 **배경색**
```html
<!-- 어두운 배경 -->
<div class="bg-slate-900">가장 어두운 배경</div>
<div class="bg-slate-800">카드 배경</div>
<div class="bg-slate-700">버튼 배경</div>

<!-- 네온 보라색 -->
<div class="bg-purple-600">네온 보라</div>
<div class="bg-purple-700">진한 보라</div>

<!-- 그라데이션 -->
<div class="bg-gradient-to-r from-purple-600 to-pink-600">그라데이션</div>
```

### ✨ **글자색**
```html
<p class="text-white">하얀 글자</p>
<p class="text-gray-300">회색 글자</p>
<p class="text-purple-400">보라 글자</p>
<p class="text-red-400">빨간 글자 (에러)</p>
<p class="text-green-400">초록 글자 (성공)</p>
```

---

## 🔤 **글자 크기 & 스타일**

### 📝 **글자 크기**
```html
<h1 class="text-4xl font-bold">큰 제목</h1>
<h2 class="text-2xl font-semibold">중간 제목</h2>
<h3 class="text-xl font-medium">작은 제목</h3>
<p class="text-base">일반 본문</p>
<p class="text-sm text-gray-400">작은 설명</p>
```

### 💪 **글자 굵기**
```html
<p class="font-normal">일반</p>
<p class="font-medium">중간</p>
<p class="font-semibold">약간 굵게</p>
<p class="font-bold">굵게</p>
```

---

## 🔘 **버튼 스타일**

### 🎮 **게임용 버튼**
```html
<!-- 기본 네온 버튼 -->
<button class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-300 hover:scale-105">
  플레이
</button>

<!-- 큰 스핀 버튼 -->
<button class="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-full text-xl font-bold shadow-lg hover:shadow-purple-500/50 transition-all duration-300">
  🎰 SPIN
</button>

<!-- 작은 버튼 -->
<button class="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded text-sm transition-colors">
  설정
</button>

<!-- 테두리만 있는 버튼 -->
<button class="border-2 border-purple-500 text-purple-400 hover:bg-purple-500 hover:text-white px-4 py-2 rounded transition-all">
  취소
</button>
```

---

## 🃏 **카드 스타일**

### 🎨 **기본 카드**
```html
<!-- 게임 카드 -->
<div class="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-purple-500 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-300 cursor-pointer">
  <h3 class="text-xl font-semibold text-white mb-2">슬롯 머신</h3>
  <p class="text-gray-400 mb-4">운을 시험해보세요!</p>
  <button class="w-full bg-purple-600 text-white py-2 rounded-lg">플레이</button>
</div>

<!-- 글로우 효과 카드 -->
<div class="bg-slate-800 border border-purple-500 rounded-xl p-6 shadow-lg shadow-purple-500/30">
  <div class="text-center">
    <p class="text-purple-400 text-sm">VIP 전용</p>
    <h3 class="text-2xl font-bold text-white">프리미엄 게임</h3>
  </div>
</div>
```

---

## 📱 **반응형 (모바일 대응)**

### 🔧 **화면 크기별 다르게**
```html
<!-- 모바일: 세로배치, 데스크톱: 가로배치 -->
<div class="flex flex-col lg:flex-row gap-4">
  <div class="lg:w-1/3">사이드바</div>
  <div class="lg:w-2/3">메인 콘텐츠</div>
</div>

<!-- 모바일: 숨김, 데스크톱: 보임 -->
<div class="hidden lg:block">데스크톱에서만 보임</div>
<div class="lg:hidden">모바일에서만 보임</div>

<!-- 글자 크기 반응형 -->
<h1 class="text-2xl lg:text-4xl">모바일 작게, 데스크톱 크게</h1>
```

---

## ✨ **특수 효과**

### 🌟 **호버 효과**
```html
<!-- 마우스 올리면 커짐 -->
<div class="transform hover:scale-105 transition-transform duration-300">
  커지는 카드
</div>

<!-- 마우스 올리면 떠오름 -->
<div class="hover:-translate-y-2 transition-transform duration-300">
  떠오르는 카드
</div>

<!-- 네온 글로우 -->
<div class="hover:shadow-lg hover:shadow-purple-500/50 transition-shadow duration-300">
  글로우 효과
</div>
```

### 🎭 **애니메이션**
```html
<!-- 페이드 인 -->
<div class="opacity-0 animate-fade-in">서서히 나타남</div>

<!-- 스핀 (로딩) -->
<div class="animate-spin w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full">
</div>

<!-- 펄스 (깜빡임) -->
<div class="animate-pulse bg-purple-600 p-4 rounded">
  깜빡이는 효과
</div>
```

---

## 🎯 **자주 쓰는 조합**

### 🎮 **게임 토큰 표시**
```html
<div class="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-full">
  <span class="text-yellow-400">💰</span>
  <span class="text-white font-mono text-lg">1,234</span>
  <span class="text-gray-400 text-sm">코인</span>
</div>
```

### 📊 **프로그레스 바**
```html
<div class="w-full bg-slate-700 rounded-full h-3">
  <div class="bg-gradient-to-r from-green-500 to-green-400 h-3 rounded-full transition-all duration-500" style="width: 70%">
  </div>
</div>
```

### 🔔 **알림 메시지**
```html
<!-- 성공 -->
<div class="bg-green-900 border border-green-500 text-green-200 px-4 py-3 rounded-lg">
  ✅ 게임에서 승리했습니다!
</div>

<!-- 에러 -->
<div class="bg-red-900 border border-red-500 text-red-200 px-4 py-3 rounded-lg">
  ❌ 토큰이 부족합니다.
</div>

<!-- 정보 -->
<div class="bg-blue-900 border border-blue-500 text-blue-200 px-4 py-3 rounded-lg">
  ℹ️ 새로운 게임이 추가되었습니다.
</div>
```

---

## 🛠 **빠른 복사용 템플릿**

### 🎯 **완전한 게임 카드**
```html
<div class="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-purple-500 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-300 cursor-pointer transform hover:scale-105">
  <!-- 카드 헤더 -->
  <div class="flex justify-between items-start mb-4">
    <h3 class="text-xl font-semibold text-white">슬롯 머신</h3>
    <span class="bg-purple-600 text-white text-xs px-2 py-1 rounded-full">신규</span>
  </div>
  
  <!-- 카드 내용 -->
  <p class="text-gray-400 mb-4">운을 시험해보세요! 잭팟을 노려보세요.</p>
  
  <!-- 게임 정보 -->
  <div class="flex justify-between text-sm text-gray-500 mb-4">
    <span>최소 베팅: 10 코인</span>
    <span>최대 배당: 1000x</span>
  </div>
  
  <!-- 플레이 버튼 -->
  <button class="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-300">
    🎰 플레이 시작
  </button>
</div>
```

### 🎮 **완전한 게임 헤더**
```html
<header class="bg-slate-900 border-b border-slate-700 p-4">
  <div class="flex justify-between items-center max-w-6xl mx-auto">
    <!-- 로고 -->
    <div class="flex items-center gap-2">
      <span class="text-2xl">🎰</span>
      <h1 class="text-xl font-bold text-white">Casino Club</h1>
    </div>
    
    <!-- 토큰 표시 -->
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-full">
        <span class="text-yellow-400">💰</span>
        <span class="text-white font-mono text-lg">1,234</span>
      </div>
      
      <!-- 프로필 -->
      <div class="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
        <span class="text-white text-sm font-bold">P</span>
      </div>
    </div>
  </div>
</header>
```

---

## 💡 **사용 팁**

### ✅ **이것만 기억하세요!**

1. **간격**: `p-4` (32px), `m-4` (32px), `gap-4` (16px 간격)
2. **색상**: `bg-slate-800` (어두운 배경), `text-white` (흰 글자)
3. **호버**: `hover:` 붙이면 마우스 올릴 때 효과
4. **반응형**: `lg:` 붙이면 큰 화면에서만 적용
5. **애니메이션**: `transition-all duration-300` 부드러운 효과

### 🚀 **바로 사용하는 방법**
1. 위 코드를 그대로 복사
2. HTML 파일에 붙여넣기  
3. Tailwind CSS 설정되어 있으면 바로 작동!

---

## 🎯 **자주 묻는 질문**

**Q: 색깔을 바꾸고 싶어요**
```html
<!-- 보라색 → 파란색 -->
bg-purple-600 → bg-blue-600
text-purple-400 → text-blue-400
```

**Q: 크기를 바꾸고 싶어요**
```html
<!-- 패딩 작게 → 크게 -->
p-4 → p-6 또는 p-8
<!-- 글자 작게 → 크게 -->
text-base → text-lg 또는 text-xl
```

**Q: 반응형이 안 돼요**
```html
<!-- 모바일 기본, 큰 화면에서 변경 -->
<div class="text-sm lg:text-lg">반응형 글자</div>
```

---

**🎉 이제 바로 복사해서 사용하세요!** 

*고등학생도 5분만에 예쁜 게임 UI 만들기 완료!* ✨
