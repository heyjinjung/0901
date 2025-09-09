# 🤝 Casino-Club F2P 기여 가이드

Casino-Club F2P 프로젝트에 기여해주셔서 감사합니다! 이 가이드는 프로젝트에 효과적으로 기여하는 방법을 안내합니다.

## 🚀 시작하기

### 개발 환경 요구사항
- **Docker & Docker Compose**: 필수
- **Git**: 버전 관리
- **PowerShell**: Windows 환경 (스크립트 실행용)
- **Visual Studio Code**: 권장 IDE

### 로컬 개발 환경 설정
```bash
# 1. 저장소 포크 및 클론
git clone https://github.com/YOUR-USERNAME/auto7777.git
cd auto7777

# 2. upstream 원격 저장소 추가
git remote add upstream https://github.com/mamam1281/auto7777.git

# 3. 개발 환경 설정
.\docker-manage.ps1 setup

# 4. 서비스 시작
.\docker-manage.ps1 start --tools
```

## 📋 기여 방법

### 1. 이슈 확인 및 생성
- [기존 이슈](https://github.com/mamam1281/auto7777/issues) 확인
- 새로운 기능이나 버그 발견 시 이슈 생성
- 이슈 템플릿을 사용하여 상세한 정보 제공

### 2. 브랜치 생성
```bash
# main 브랜치에서 최신 코드 동기화
git checkout main
git pull upstream main

# 기능별 브랜치 생성
git checkout -b feature/your-feature-name
# 또는
git checkout -b fix/issue-description
```

### 3. 개발 및 테스트
```powershell
# 개발 서버 실행
.\docker-manage.ps1 start --tools

# 테스트 실행
.\docker-manage.ps1 test coverage

# 특정 서비스 테스트
.\docker-manage.ps1 test backend
.\docker-manage.ps1 test frontend
```

### 4. 커밋 및 푸시
```bash
# 변경사항 스테이징
git add .

# 커밋 (규칙에 따라)
git commit -m "feat: add slot machine multiplier system"

# 브랜치 푸시
git push origin feature/your-feature-name
```

### 5. Pull Request 생성
- GitHub에서 Pull Request 생성
- PR 템플릿에 따라 상세한 설명 작성
- 관련 이슈 링크 연결

## 🎯 개발 영역별 가이드

### 🎮 게임 시스템 개발

#### 새로운 게임 추가
```typescript
// 1. 게임 컴포넌트 생성
// cc-webapp/frontend/components/games/newgame/NewGame.tsx

interface NewGameProps {
  user: User;
  onGameComplete: (result: GameResult) => void;
}

export default function NewGame({ user, onGameComplete }: NewGameProps) {
  // 게임 로직 구현
}
```

```python
# 2. 백엔드 API 추가
# cc-webapp/backend/app/api/routes/games.py

@router.post("/newgame/play")
async def play_new_game(
    request: NewGameRequest,
    user: User = Depends(get_current_user)
):
    # 게임 로직 처리
    return GameResult(...)
```

#### 게임 개발 체크리스트
- [ ] RNG (Random Number Generator) 구현
- [ ] 가변 비율 보상 시스템 적용
- [ ] 니어 미스 효과 구현
- [ ] 도파민 피드백 연동
- [ ] 모바일 반응형 UI
- [ ] 접근성 고려 (ARIA)
- [ ] 단위 테스트 작성

### 💎 경제 시스템 개발

#### 새로운 화폐 또는 보상 시스템
```python
# 1. 데이터베이스 모델 추가
class NewCurrency(SQLAlchemyModel):
    __tablename__ = "new_currencies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(default=0)
    last_updated: Mapped[datetime] = mapped_column(default=func.now())
```

```typescript
// 2. 프론트엔드 타입 정의
interface NewCurrency {
  id: number;
  userId: number;
  amount: number;
  lastUpdated: string;
}
```

### 🧠 개인화 시스템 개발

#### 새로운 추천 알고리즘 추가
```python
# cc-webapp/backend/app/services/recommendation_service.py

async def generate_new_recommendations(
    user_segment: UserSegment,
    context: RecommendationContext
) -> List[Recommendation]:
    """
    새로운 추천 알고리즘 구현
    """
    # 추천 로직 구현
    pass
```

### 🎨 UI/UX 개발

#### 새로운 컴포넌트 추가
```typescript
// cc-webapp/frontend/components/ui/NewComponent.tsx

interface NewComponentProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export function NewComponent({ variant = 'primary', size = 'md', children }: NewComponentProps) {
  return (
    <div className={cn(
      "base-styles",
      {
        "variant-primary": variant === 'primary',
        "variant-secondary": variant === 'secondary',
        "size-sm": size === 'sm',
        "size-md": size === 'md',
        "size-lg": size === 'lg'
      }
    )}>
      {children}
    </div>
  );
}
```

## 📏 코딩 표준

### 백엔드 (Python/FastAPI)

#### 디렉토리 구조
```
app/
├── api/
│   └── routes/          # API 라우터
├── core/
│   ├── config.py        # 설정
│   ├── database.py      # DB 연결
│   └── security.py      # 보안
├── models/              # SQLAlchemy 모델
├── schemas/             # Pydantic 스키마
├── services/            # 비즈니스 로직
└── utils/               # 유틸리티
```

#### 코딩 스타일
```python
# PEP 8 준수
# Type hints 사용
from typing import Optional, List
from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int
    nickname: str
    email: Optional[str] = None
    
    class Config:
        from_attributes = True

# 의존성 주입 활용
async def get_user_service(
    db: AsyncSession = Depends(get_db)
) -> UserService:
    return UserService(db)

# 예외 처리
@router.post("/users/")
async def create_user(
    user_data: UserCreateSchema,
    service: UserService = Depends(get_user_service)
) -> UserSchema:
    try:
        user = await service.create_user(user_data)
        return UserSchema.from_orm(user)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 프론트엔드 (TypeScript/React)

#### 디렉토리 구조
```
components/
├── games/               # 게임별 컴포넌트
├── profile/             # 프로필 시스템
├── ui/                  # 재사용 가능한 UI
└── layout/              # 레이아웃 컴포넌트
```

#### 코딩 스타일
```typescript
// TypeScript 엄격 모드
interface ComponentProps {
  title: string;
  description?: string;
  onAction: (data: ActionData) => void;
}

// 함수형 컴포넌트 + Hooks
export default function Component({ title, description, onAction }: ComponentProps) {
  const [isLoading, setIsLoading] = useState(false);
  
  // Custom hooks 활용
  const { user, updateUser } = useUser();
  
  // 이벤트 핸들러
  const handleAction = useCallback(async (data: ActionData) => {
    setIsLoading(true);
    try {
      await onAction(data);
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [onAction]);

  // 조건부 렌더링
  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="component-container">
      <h2 className="component-title">{title}</h2>
      {description && (
        <p className="component-description">{description}</p>
      )}
    </div>
  );
}
```

### CSS/Styling (Tailwind CSS v4)
```css
/* 커스텀 유틸리티 클래스 */
.glass-effect {
  @apply bg-white/5 backdrop-blur-sm border border-white/10;
}

.text-gradient-primary {
  @apply bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent;
}

/* 애니메이션 */
@keyframes neon-pulse {
  0%, 100% { box-shadow: 0 0 20px var(--color-neon-purple); }
  50% { box-shadow: 0 0 40px var(--color-neon-purple); }
}

.neon-pulse {
  animation: neon-pulse 2s ease-in-out infinite;
}
```

## 🧪 테스트 가이드

### 백엔드 테스트 (Pytest)
```python
# tests/test_user_service.py
import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreateSchema

@pytest.mark.asyncio
async def test_create_user(db_session):
    service = UserService(db_session)
    user_data = UserCreateSchema(
        nickname="testuser",
        email="test@example.com"
    )
    
    user = await service.create_user(user_data)
    
    assert user.nickname == "testuser"
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_user_by_id(db_session):
    # 테스트 구현
    pass
```

### 프론트엔드 테스트 (Jest + React Testing Library)
```typescript
// __tests__/components/GameCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { GameCard } from '@/components/GameCard';

describe('GameCard', () => {
  it('renders game title and description', () => {
    render(
      <GameCard 
        title="Test Game" 
        description="Test Description"
        onPlay={jest.fn()}
      />
    );
    
    expect(screen.getByText('Test Game')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('calls onPlay when play button is clicked', () => {
    const mockOnPlay = jest.fn();
    render(
      <GameCard 
        title="Test Game" 
        onPlay={mockOnPlay}
      />
    );
    
    fireEvent.click(screen.getByRole('button', { name: /play/i }));
    expect(mockOnPlay).toHaveBeenCalledTimes(1);
  });
});
```

## 📝 커밋 메시지 규칙

### 형식
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 타입
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포매팅, 세미콜론 누락 등
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 작업, 패키지 관리
- `perf`: 성능 개선
- `ci`: CI 설정 변경

### 예시
```
feat(games): add slot machine bonus rounds

- Implement free spin feature
- Add multiplier system for bonus rounds
- Update UI for bonus round display

Closes #123
```

## 🔍 코드 리뷰 가이드

### Pull Request 체크리스트
- [ ] 기능이 정상적으로 동작하는가?
- [ ] 테스트가 추가되었고 모든 테스트가 통과하는가?
- [ ] 코딩 표준을 준수하는가?
- [ ] 문서가 업데이트되었는가?
- [ ] 성능에 영향을 주지 않는가?
- [ ] 보안 취약점이 없는가?
- [ ] 접근성을 고려했는가?

### 리뷰어 가이드라인
- 건설적이고 친근한 피드백 제공
- 코드의 의도를 이해하려고 노력
- 대안 제시 시 이유 설명
- 칭찬도 잊지 않기

## 🚀 배포 가이드

### 개발 환경
```powershell
# 개발 서버 시작
.\docker-manage.ps1 start --tools

# 서비스 상태 확인
.\docker-manage.ps1 status
```

### 스테이징 환경
```powershell
# 스테이징 배포
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

### 프로덕션 환경
```powershell
# 프로덕션 배포
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📞 도움 요청

### 이슈 생성 가이드
1. 기존 이슈 검색
2. 적절한 이슈 템플릿 선택
3. 상세한 정보 제공:
   - 환경 정보
   - 재현 단계
   - 기대 결과 vs 실제 결과
   - 스크린샷 (UI 관련)

### 커뮤니티
- [GitHub Discussions](https://github.com/mamam1281/auto7777/discussions)
- [이슈 트래커](https://github.com/mamam1281/auto7777/issues)

---

Casino-Club F2P 프로젝트에 기여해주셔서 다시 한 번 감사드립니다! 🎰✨
