"""
초대 코드 검증 및 관리 서비스
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import random
import string
import hashlib
import secrets
from app.models.auth_models import InviteCode
from app.core.exceptions import UserServiceException

class InviteService:
    """초대코드 서비스"""
    
    # 항상 사용 가능한 고정 코드 정의
    FIXED_CODES = ["6969", "6974", "2560"]
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_invite_code(self, code: str) -> Dict[str, Any]:
        """
        초대코드 유효성 검증
        Args:
            code: 검증할 초대코드
        Returns:
            유효성 검증 결과
        Raises:
            UserServiceException: 초대코드가 유효하지 않은 경우
        """
        # 고정 초대코드인 경우 항상 유효
        if code in self.FIXED_CODES:
            # 데이터베이스에 없으면 자동 추가
            invite_code = self.db.query(InviteCode).filter(InviteCode.code == code).first()
            if not invite_code:
                invite_code = InviteCode(
                    code=code,
                    is_used=False,
                    created_at=datetime.utcnow(),
                    expires_at=None,  # 만료 없음
                    max_uses=None,    # 무제한 사용
                    used_count=0
                )
                self.db.add(invite_code)
                self.db.commit()
                self.db.refresh(invite_code)
            
            return {
                "valid": True,
                "code": code,
                "created_at": invite_code.created_at if invite_code else datetime.utcnow(),
                "expires_at": None,
                "max_uses": None,
                "use_count": invite_code.used_count if invite_code else 0,
                "is_special": True
            }
        
        # 일반 초대코드 검증 로직
        invite_code = self.db.query(InviteCode).filter(InviteCode.code == code).first()
        
        # 존재하지 않는 코드
        if not invite_code:
            raise UserServiceException(f"초대코드 {code}가 존재하지 않습니다.", "INVALID_INVITE_CODE")
        
        # 이미 사용된 코드
        if invite_code.is_used:
            raise UserServiceException(f"초대코드 {code}는 이미 사용되었습니다.", "USED_INVITE_CODE")
        
        # 만료된 코드 검증
        now = datetime.utcnow()
        if invite_code.expires_at and invite_code.expires_at < now:
            raise UserServiceException(f"초대코드 {code}는 만료되었습니다.", "EXPIRED_INVITE_CODE")
        
        # 사용 횟수 제한 검증
        if invite_code.max_uses is not None and invite_code.used_count >= invite_code.max_uses:
            raise UserServiceException(f"초대코드 {code}의 사용 횟수가 초과되었습니다.", "MAX_USES_EXCEEDED")
        
        # 유효한 코드 반환
        return {
            "valid": True,
            "code": invite_code.code,
            "created_at": invite_code.created_at,
            "expires_at": invite_code.expires_at,
            "max_uses": invite_code.max_uses,
            "use_count": invite_code.used_count,
            "is_special": invite_code.code in self.FIXED_CODES
        }
    
    def use_invite_code(self, code: str, user_id: int) -> bool:
        """
        초대코드 사용 처리
        Args:
            code: 사용할 초대코드
            user_id: 코드를 사용한 사용자 ID
        Returns:
            처리 결과
        """
        # 고정 초대코드인 경우 무제한 사용 가능
        if code in self.FIXED_CODES:
            invite_code = self.db.query(InviteCode).filter(InviteCode.code == code).first()
            if not invite_code:
                # 고정 코드가 DB에 없으면 추가
                invite_code = InviteCode(
                    code=code,
                    is_used=False,
                    created_at=datetime.utcnow(),
                    expires_at=None,
                    max_uses=None,
                    used_count=0
                )
                self.db.add(invite_code)
            
            # 사용 카운트만 증가시키고 is_used는 변경하지 않음
            invite_code.used_count += 1
            invite_code.used_at = datetime.utcnow()
            invite_code.used_by_user_id = user_id
            self.db.commit()
            return True
        
        # 일반 초대코드 처리 로직
        invite_code = self.db.query(InviteCode).filter(InviteCode.code == code).first()
        
        # 존재하지 않는 코드
        if not invite_code:
            return False
        
        # 만료 확인
        now = datetime.utcnow()
        if invite_code.expires_at and invite_code.expires_at < now:
            return False
        
        # 사용 횟수 제한 확인
        if invite_code.max_uses is not None and invite_code.used_count >= invite_code.max_uses:
            return False
        
        # 일회용 코드인 경우
        if invite_code.max_uses == 1:
            invite_code.is_used = True
        
        # 초대코드 사용 처리
        invite_code.used_at = datetime.utcnow()
        invite_code.used_count += 1
        invite_code.used_by_user_id = user_id
        self.db.commit()
        return True
    
    def get_invite_code(self, code: str) -> Optional[InviteCode]:
        """
        초대코드 조회
        Args:
            code: 조회할 초대코드
        Returns:
            초대코드 정보
        """
        # 고정 코드인 경우 없으면 생성
        if code in self.FIXED_CODES:
            invite_code = self.db.query(InviteCode).filter(InviteCode.code == code).first()
            if not invite_code:
                invite_code = InviteCode(
                    code=code,
                    is_used=False,
                    created_at=datetime.utcnow(),
                    expires_at=None,
                    max_uses=None,
                    used_count=0
                )
                self.db.add(invite_code)
                self.db.commit()
                self.db.refresh(invite_code)
            return invite_code
        
        return self.db.query(InviteCode).filter(InviteCode.code == code).first()
    
    def list_invite_codes(self, limit: int = 10, offset: int = 0) -> List[InviteCode]:
        """
        초대코드 목록 조회
        Args:
            limit: 조회 제한
            offset: 조회 시작점
        Returns:
            초대코드 목록
        """
        return self.db.query(InviteCode).order_by(InviteCode.created_at.desc()).offset(offset).limit(limit).all()
        
    def generate_secure_invite_code(self, length: int = 6, max_uses: int = 1, days_valid: int = 30) -> InviteCode:
        """
        보안성 높은 초대코드 생성
        Args:
            length: 코드 길이
            max_uses: 최대 사용 횟수 (None은 무제한)
            days_valid: 유효 기간 (일)
        Returns:
            생성된 초대코드
        Notes:
            - 안전한 난수 생성기 사용 (secrets 모듈)
            - 중복 확인 절차
            - 유효기간 및 사용 횟수 제한 설정
        """
        # 초대코드 문자셋 정의 (혼동하기 쉬운 문자 제외)
        charset = string.ascii_uppercase + string.digits
        charset = charset.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
        
        # 초대코드 생성
        while True:
            # 보안 난수 생성기 사용
            code = ''.join(secrets.choice(charset) for _ in range(length))
            
            # 고정 코드와 충돌 방지
            if code in self.FIXED_CODES:
                continue
                
            # 중복 확인
            existing = self.db.query(InviteCode).filter(InviteCode.code == code).first()
            if not existing:
                break
        
        # 만료일 설정
        expires_at = datetime.utcnow() + timedelta(days=days_valid) if days_valid else None
        
        # 초대코드 생성
        invite_code = InviteCode(
            code=code,
            is_used=False,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            max_uses=max_uses,
            used_count=0
        )
        
        # DB에 저장
        self.db.add(invite_code)
        self.db.commit()
        self.db.refresh(invite_code)
        
        return invite_code
    
    def generate_bulk_invite_codes(self, count: int = 10, length: int = 6, max_uses: int = 1, days_valid: int = 30) -> List[InviteCode]:
        """
        대량 초대코드 생성
        Args:
            count: 생성할 코드 수
            length: 코드 길이
            max_uses: 최대 사용 횟수 (None은 무제한)
            days_valid: 유효 기간 (일)
        Returns:
            생성된 초대코드 목록
        """
        result = []
        for _ in range(count):
            result.append(self.generate_secure_invite_code(length, max_uses, days_valid))
        return result
