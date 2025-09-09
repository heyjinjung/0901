"""기본 관리자/유저 4명 시드 스크립트 (멱등)

사용:
    docker compose exec backend python -m app.scripts.seed_basic_accounts

계정 목록:
  관리자: site_id=admin  nickname=어드민  pw=123456  is_admin=True
  유저:   site_id=user001..user004  nickname=유저01..유저04  pw=123455
조건:
  - 존재하면 비밀번호만 재동기화(옵션) 및 is_admin 보정
  - invite_code 기본 '5858'
  - phone_number 필수 → 패턴 0100000XXXX 사용
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.auth_models import User
from app.services.auth_service import AuthService

ADMIN_SPEC = {
    'site_id': 'admin',
    'nickname': '어드민',
    'password': '123456',
    'is_admin': True,
}

USER_SPECS = [
    {'site_id': f'user{n:03d}', 'nickname': f'유저{n:02d}', 'password': '123455'}
    for n in range(1,5)
]

INVITE_CODE = '5858'


def _alloc_phone(sess, base: str) -> str:
    """주어진 base 번호(예: '0100000') + 증가 숫자 붙여 UNIQUE 충돌 회피.
    기존 구현은 고정 번호 사용 → UniqueViolation 발생 가능. 최대 50회 시도.
    """
    from sqlalchemy import text
    for i in range(0, 50):
        candidate = f"{base}{i:02d}"
        # 빠른 존재 확인 (인덱스 기대: phone_number UNIQUE)
        exists = sess.execute(text("SELECT 1 FROM users WHERE phone_number=:p LIMIT 1"), {"p": candidate}).scalar()
        if not exists:
            return candidate
    # fallback: 매우 드문 케이스 → random suffix
    import random
    return f"{base}{random.randint(5000,9999)}"


def ensure_user(sess, spec, *, refresh_password: bool = True):
    site_id = spec['site_id']
    user = sess.execute(select(User).where(User.site_id == site_id)).scalar_one_or_none()
    raw_pw = spec['password']
    if user is None:
        base_phone = '0100000'
        if site_id.startswith('user'):
            # user001 → 뒤 3자리 활용하되 중복 시 _alloc_phone 로 재할당
            guess = f"0100000{site_id[-3:]}"
        else:
            guess = '01000000000'
        # 충돌 회피
        phone = guess
        from sqlalchemy import text
        exists = sess.execute(text("SELECT 1 FROM users WHERE phone_number=:p LIMIT 1"), {"p": phone}).scalar()
        if exists:
            phone = _alloc_phone(sess, base_phone)
        user = User(
            site_id=site_id,
            nickname=spec['nickname'],
            phone_number=phone,
            invite_code=INVITE_CODE,
            password_hash=AuthService.get_password_hash(raw_pw),
            is_admin=spec.get('is_admin', False),
        )
        sess.add(user)
        action = 'created'
    else:
        # 비밀번호 재설정 및 admin 플래그 동기화(필요 시)
        updated = False
        if spec.get('is_admin') and not user.is_admin:
            user.is_admin = True
            updated = True
        if refresh_password:
            user.password_hash = AuthService.get_password_hash(raw_pw)
        action = 'updated' if updated else 'refreshed'
    return user, action


def main(refresh_password: bool = True):
    """기본 계정 시드 (멱등 및 phone 중복 회피).

    Args:
        refresh_password: 기존 계정 존재 시 비밀번호 재설정 여부
    """
    sess = SessionLocal()
    results = []
    try:
        u, a = ensure_user(sess, ADMIN_SPEC, refresh_password=refresh_password)
        results.append({'site_id': u.site_id, 'action': a, 'is_admin': u.is_admin})
        for spec in USER_SPECS:
            u, a = ensure_user(sess, spec, refresh_password=refresh_password)
            results.append({'site_id': u.site_id, 'action': a, 'is_admin': u.is_admin})
        try:
            sess.commit()
        except IntegrityError as ie:
            sess.rollback()
            print(f"[seed_basic_accounts] IntegrityError: {ie}")
            return {'ok': False, 'error': 'integrity', 'details': str(ie), 'partial': results}
        print({'ok': True, 'results': results})
        return {'ok': True, 'results': results}
    except Exception as e:  # pragma: no cover
        sess.rollback()
        print({'ok': False, 'error': type(e).__name__, 'details': str(e)})
        raise
    finally:
        sess.close()


if __name__ == '__main__':  # pragma: no cover
    main()
