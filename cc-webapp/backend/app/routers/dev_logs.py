from fastapi import APIRouter, Request, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.config import settings
from app.models.auth_models import User
from datetime import datetime

router = APIRouter(prefix="/api/dev", tags=["dev"], include_in_schema=False)


@router.post('/logs', status_code=status.HTTP_204_NO_CONTENT)
async def receive_logs(request: Request):
    """개발용: 프론트에서 전송하는 디버그/추적 로그를 수신합니다. 프로덕션에 포함 금지."""
    try:
        payload = await request.json()
    except Exception:
        payload = await request.body()
    # 간단히 로그에 출력합니다. 운영 환경에서는 파일/외부 수집기로 전송하도록 변경하세요.
    try:
        print('[dev_logs] received logs:')
        print(payload)
    except Exception:
        pass
    return None


@router.post('/reset_user02')
async def reset_user02(db: Session = Depends(get_db)):
    """개발 전용: user id=2 (user02) 상태 초기화 / 존재하지 않으면 생성.

    수행 내용:
    - ENVIRONMENT 이 development 가 아니면 403
    - 사용자(id=2) 없으면 생성(site_id/nickname=user02)
    - gold_balance=1000, rank STANDARD, 기본 프로필 값 초기화
    - 연관 활동/보상/세션 테이블 데이터 정리 (존재 시) - 대량 삭제 (성능 고려, synchronize_session=False)
    - updated_at 갱신
    반환: {action: created|reset, deleted: {actions,rewards,sessions}, user_id, gold_balance}
    """
    if settings.ENVIRONMENT not in ("development", "local", "dev"):
        raise HTTPException(status_code=403, detail="development only")

    # 필수 테이블 이름들 (존재하지 않을 수도 있으니 예외 무시)
    delete_counts = {"actions": 0, "rewards": 0, "sessions": 0}
    action = "reset"
    user = db.query(User).filter(User.id == 2).first()
    if not user:
        # user02 생성
        user = User(
            id=2,  # 고정 ID (개발 DB 가정) - 충돌 시 자동 증가 DB 에서는 실패 가능
            site_id="user02",
            nickname="user02",
            phone_number="0000000000",
            password_hash="dev_reset_placeholder",
            invite_code=settings.UNLIMITED_INVITE_CODE or "5858",
            gold_balance=1000,
            user_rank="STANDARD",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        try:
            db.add(user)
            db.flush()
            action = "created"
        except Exception as e:
            # ID 고정 삽입 실패 시 fallback: 기존 행 찾기(경합) 또는 abort
            db.rollback()
            # 재시도 (경합으로 이미 생성되었을 가능성)
            user = db.query(User).filter(User.site_id == "user02").first()
            if not user:
                raise HTTPException(status_code=500, detail=f"failed to create user02: {e}")

    # 연관 데이터 삭제 (존재하지 않을 경우 무시)
    try:
        for model_name, key in [
            ("UserAction", "actions"),
            ("UserReward", "rewards"),
            ("UserSession", "sessions"),
        ]:
            model = getattr(__import__("app.models.game_models", fromlist=[model_name]), model_name, None)
            if not model:
                # 일부 모델은 다른 파일(auth_models)에 존재
                if model_name == "UserSession":
                    from app.models.auth_models import UserSession as US
                    model = US
                else:
                    continue
            try:
                cnt = db.query(model).filter(getattr(model, 'user_id') == user.id).delete(synchronize_session=False)
                delete_counts[key] = cnt
            except Exception:
                pass
    except Exception:
        pass

    # 사용자 필드 재설정
    user.nickname = "user02"
    user.phone_number = "0000000000"
    user.gold_balance = 1000
    user.user_rank = "STANDARD"
    user.updated_at = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"reset failed: {e}")

    return {
        "success": True,
        "action": action,
        "user_id": user.id,
        "gold_balance": user.gold_balance,
        "deleted": delete_counts,
    }
