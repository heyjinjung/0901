import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.auth_models import User
from app.services.currency_service import CurrencyService, InsufficientBalanceError
from app.database import Base

# 간단한 인메모리 DB 기반 단위 테스트
@pytest.fixture()
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    u = User(site_id='u1', nickname='u1', phone_number='010', password_hash='x', invite_code='5858')
    session.add(u)
    session.commit()
    yield session
    session.close()


def test_add_and_deduct_gem(db_session):
    svc = CurrencyService(db_session)
    uid = db_session.query(User).first().id
    bal = svc.add(uid, 100, 'gem')
    assert bal == 100
    bal2 = svc.deduct(uid, 40, 'gem')
    assert bal2 == 60


def test_insufficient_gem(db_session):
    svc = CurrencyService(db_session)
    uid = db_session.query(User).first().id
    with pytest.raises(InsufficientBalanceError):
        svc.deduct(uid, 10, 'gem')


def test_add_coin(db_session):
    svc = CurrencyService(db_session)
    uid = db_session.query(User).first().id
    bal = svc.add(uid, 55, 'coin')
    assert bal == 55
