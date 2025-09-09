import pytest
from fastapi import FastAPI, Query
from fastapi.testclient import TestClient

from app.core.error_handlers import add_exception_handlers
from app.core.exceptions import NotFoundError, ValidationError

app = FastAPI()
add_exception_handlers(app)

@app.get('/raise/notfound')
async def raise_notfound():
    raise NotFoundError("resource missing")

@app.get('/validate-int')
async def validate_int(limit: int = Query(..., ge=1, le=10)):
    return {"limit": limit}

@app.get('/validate-domain')
async def validate_domain(flag: str):
    if flag not in {"A", "B"}:
        raise ValidationError("flag must be A or B", details={"allowed": ["A","B"], "received": flag})
    return {"flag": flag}

client = TestClient(app)

def assert_error_schema(resp, code: str):
    assert resp.status_code >= 400
    body = resp.json()
    assert 'error' in body
    err = body['error']
    assert err['code'] == code
    assert 'message' in err
    assert 'request_id' in err
    # details optional


def test_notfound_error_envelope():
    r = client.get('/raise/notfound')
    assert_error_schema(r, 'NOT_FOUND')


def test_pydantic_validation_envelope():
    r = client.get('/validate-int', params={'limit': 0})
    assert_error_schema(r, 'VALIDATION_ERROR')


def test_domain_validation_error_envelope():
    r = client.get('/validate-domain', params={'flag': 'X'})
    assert_error_schema(r, 'VALIDATION_ERROR')
    data = r.json()['error']
    assert data['details']['allowed'] == ["A","B"]
    assert data['details']['received'] == 'X'
