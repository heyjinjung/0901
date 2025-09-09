import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.core.error_handlers import add_exception_handlers
from app.core.exceptions import BaseDomainError, ValidationError, NotFoundError

app = FastAPI()
add_exception_handlers(app)

@app.get('/raise/domain')
async def raise_domain():
    raise NotFoundError("X not found")

@app.get('/raise/http')
async def raise_http():
    raise HTTPException(status_code=418, detail='teapot')

@app.get('/ok')
async def ok():
    return {"ok": True}

client = TestClient(app)

def assert_error(resp, code: str):
    assert resp.status_code >= 400
    data = resp.json()
    assert 'error' in data
    assert data['error']['code'] == code
    assert 'request_id' in data['error']


def test_domain_error_schema():
    r = client.get('/raise/domain')
    assert_error(r, 'NOT_FOUND')


def test_http_error_schema():
    r = client.get('/raise/http')
    assert_error(r, 'HTTP_418')


def test_validation_error_schema():
    r = client.get('/ok', params={'a': 1})  # no validation here; craft one below
    # create dynamic route with validation
    @app.get('/validate')
    async def validate(limit: int):
        return {"limit": limit}
    r2 = client.get('/validate', params={'limit': 'not_int'})
    assert_error(r2, 'VALIDATION_ERROR')
